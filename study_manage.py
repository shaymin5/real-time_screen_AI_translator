from concurrent.futures import ThreadPoolExecutor, Future, wait, as_completed
from typing import Union, Optional
from datetime import datetime
from pathlib import Path
import time
import threading
import queue
import traceback

import pyautogui

from utils import Checker, FadeQueue
from ocr import GameOCR
from translator import Translator
from voxcpm_tts.tts.ttsplayer import TTSplayer


class Manager:
    def __init__(self) -> None:
        self.ocr_engine = GameOCR()
        self.translator = Translator()
        self.player = TTSplayer()
        self.checker: Checker = Checker()

        # 截图
        self.shot_dir: Path = Path.cwd().resolve()/"temp_screenshots"
        self.shot_prefix: str = "temp_screenshot"
        self.shot_position: tuple = tuple()
        self.shot_dir.mkdir(parents=True, exist_ok=True)
        
        # 清空截图文件夹
        for file in self.shot_dir.glob(f"{self.shot_prefix}_*"):
            try:
                file.unlink()
            except:
                pass

        # OCR
        self.ocr_results: FadeQueue = FadeQueue(5)
        self.ocr_lock = threading.Lock()

        # 翻译
        self.translate_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)
        self.translate_results: FadeQueue = FadeQueue(3)
        
        # TTS
        self.tts_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.tts_future: Optional[Future] = None
        self.tts_lock = threading.Lock()
        
        # 定时任务
        self.schedule_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.schedule_interval: float = 0.4
        self.schedule_timer: Optional[threading.Timer] = None
        
        # 主任务
        self.main_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.main_future: Optional[Future] = None
        
        # 控制标志
        self.processing = False
        self.stop_event = threading.Event()
        self.schedule_running = False

    def schedule_start(self):
        """启动定时任务"""
        print(f'定时任务入口，{self.schedule_running}')
        if not self.processing or self.schedule_running:
            return
        print('定时任务入口2')
        with threading.Lock():
            if self.schedule_running:
                return
            self.schedule_running = True
        print('定时任务入口3')
        self.schedule_start_time = time.perf_counter()
        try:
            self.shot_ocr_processing()
        except Exception as e:
            print(f"定时任务异常: {e}")
            traceback.print_exc()
        finally:
            self._schedule_next()

    def _schedule_next(self):
        """调度下一次任务"""
        if not self.processing:
            self.schedule_running = False
            return
            
        elapsed = time.perf_counter() - self.schedule_start_time
        wait_time = max(0.01, self.schedule_interval - elapsed)
        
        self.schedule_timer = threading.Timer(wait_time, self.schedule_start)
        self.schedule_timer.daemon = True
        self.schedule_timer.start()

    def _cleanup_schedule(self):
        """清理定时任务"""
        if self.schedule_timer:
            self.schedule_timer.cancel()
            self.schedule_timer = None
        self.schedule_running = False

    def shot(self) -> Optional[Path]:
        """截图"""
        if not self.shot_position or len(self.shot_position) != 4:
            print("截图位置未设置或格式错误")
            return None
            
        try:
            x1, y1, x2, y2 = self.shot_position
            width = x2 - x1
            height = y2 - y1
            
            if width <= 0 or height <= 0:
                print(f"无效的截图区域: {self.shot_position}")
                return None
                
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{self.shot_prefix}_{timestamp}.png"
            filepath = self.shot_dir / filename
            screenshot.save(filepath)
            return filepath
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def shot_ocr_processing(self):
        """截图和OCR处理"""
        try:
            shot_path = self.shot()
            if not shot_path:
                return
                
            text = self.ocr_engine.img_to_text(shot_path)
            if text and text.strip():
                self.ocr_results.put(text.strip())
                
            # 尝试删除截图文件
            try:
                shot_path.unlink()
            except:
                pass
                
        except Exception as e:
            print(f"OCR处理异常: {e}")
            traceback.print_exc()

    def translate_processing(self, text: str) -> Optional[str]:
        """翻译处理"""
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"翻译异常: {e}")
            traceback.print_exc()
            return None

    def tts(self, text: str):
        """文字转语音"""
        try:
            if text and text.strip():
                self.player.generate_and_play_streaming(text.strip())
        except Exception as e:
            print(f"TTS异常: {e}")
            traceback.print_exc()
        finally:
            with self.tts_lock:
                self.tts_future = None

    def start(self, x1, y1, x2, y2):
        """
        入参是给pyautogui的截图坐标
        """
        if self.processing:
            print("已经在运行中")
            return
            
        if x2 <= x1 or y2 <= y1:
            print("无效的截图坐标")
            return
            
        self.stop_event.clear()
        self.processing = True
        self.shot_position = (x1, y1, x2, y2)
        self.main_future = self.main_executor.submit(self.main_processing)

    def stop(self):
        """停止所有任务"""
        self.processing = False
        self.stop_event.set()
        
        # 清理定时任务
        self._cleanup_schedule()
        
        # 停止TTS播放
        self.player.stop()
        
        # 等待任务完成
        if self.main_future and not self.main_future.done():
            self.main_future.result(timeout=2)
            
        # 关闭所有线程池
        self.translate_executor.shutdown(wait=False)
        self.tts_executor.shutdown(wait=False)
        self.schedule_executor.shutdown(wait=False)
        self.main_executor.shutdown(wait=False)
        
        # 清空队列
        while not self.ocr_results.empty:
            try:
                self.ocr_results.get_nowait()
            except:
                break
                
        while not self.translate_results.empty:
            try:
                self.translate_results.get_nowait()
            except:
                break

    def main_processing(self):
        """主处理循环"""
        self.schedule_start()
        print('开始处理流程')
        
        try:
            while not self.stop_event.is_set() and self.processing:
                # 处理OCR结果
                if not self.ocr_results.empty:
                    try:
                        ocr_text = self.ocr_results.get_nowait()
                        print(f'OCR结果: {ocr_text}')
                        
                        if ocr_text and self.checker.check(ocr_text):
                            future = self.translate_executor.submit(
                                self.translate_processing, ocr_text
                            )
                            future.add_done_callback(
                                lambda f: self._on_translate_done(f)
                            )
                    except queue.Empty:
                        pass
                    except Exception as e:
                        print(f"处理OCR结果异常: {e}")
                        traceback.print_exc()
                
                # 处理翻译结果
                if not self.translate_results.empty:
                    try:
                        trans_text = self.translate_results.get_nowait()
                        print(f'翻译结果: {trans_text}')
                        
                        with self.tts_lock:
                            if trans_text and (self.tts_future is None or 
                                            self.tts_future.done()):
                                self.tts_future = self.tts_executor.submit(
                                    self.tts, trans_text
                                )
                    except queue.Empty:
                        pass
                    except Exception as e:
                        print(f"处理翻译结果异常: {e}")
                        traceback.print_exc()
                
                # 避免空转
                time.sleep(0.01)
                
        except Exception as e:
            print(f"主循环异常: {e}")
            traceback.print_exc()
        finally:
            self._cleanup_schedule()
            print('处理流程结束')

    def _on_translate_done(self, future: Future):
        """翻译完成回调"""
        try:
            result = future.result()
            if result:
                self.translate_results.put(result)
        except Exception as e:
            print(f"翻译回调异常: {e}")
            traceback.print_exc()

    def set_ocr_conf(self, exclude_set: set):
        """设置OCR配置"""
        self.ocr_engine.exclude_set = exclude_set
    
    def get_ocr_exclude_set(self) -> set:
        """获取OCR排除集"""
        return self.ocr_engine.exclude_set