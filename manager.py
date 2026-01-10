from concurrent.futures import ThreadPoolExecutor, Future
from typing import Union
from datetime import datetime
from pathlib import Path
import time
import threading

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
        self.shot_dir: Path = Path.cwd().resolve()/"temp_screenshots"  # 保存路径
        self.shot_prefix: str = "temp_screenshot"  # 截图文件名前缀
        self.shot_position: tuple = tuple()
        self.shot_dir.mkdir(parents=True, exist_ok=True) # 创建保存路径 理想情况下不会有残留图片 todo：清空文件夹

        # ocr
        self.ocr_results: FadeQueue = FadeQueue(5) # OCR结果

        # 翻译
        self.translate_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3) # 设计多线程使其可以同时翻译
        self.translate_results: FadeQueue = FadeQueue(3) # 翻译结果

        # TTS
        self.tts_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.tts_future: Union[Future, None] = None

        # 定时任务
        self.schedule_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.schedule_interval: float = 0.4 #单位为秒，定时任务的间隔时间
        self.schedule_start_time: float = time.perf_counter() # 单位为秒，存储每次定时线程开始时的时间        

        # maintask
        self.main_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)

        # 整套截图、OCR、翻译、TTS流程的运行标志
        self.processing = False

    def schedule_start(self):
        if not self.processing:
            return
        self.schedule_start_time = time.perf_counter() # 记录当前schedule开始时间
        future = self.schedule_executor.submit(self.shot_ocr_processing)
        future.add_done_callback(lambda f: self._on_schedule_done())

    def _on_schedule_done(self):
        # 计算剩余需要等待的时间,启动下一次定时任务
        now = time.perf_counter()
        elapsed = max(0.01, self.schedule_interval - (now - self.schedule_start_time)) # 至少等待0.01秒
        # print(f'on_schedule_done时间：{self.schedule_interval}，{now}，{self.schedule_start_time}，{now - self.schedule_start_time}，{elapsed}')
        timer = threading.Timer(elapsed, self.schedule_start)
        timer.daemon = True
        timer.start()
        
    def shot(self) -> Path:
        x1 = self.shot_position[0]
        y1 = self.shot_position[1]
        x2 = self.shot_position[2]
        y2 = self.shot_position[3]
        # 计算截图区域
        width = x2 - x1
        height = y2 - y1
        screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{self.shot_prefix}_{timestamp}.png"
        filepath = self.shot_dir / filename
        # 保存图片
        screenshot.save(filepath)
        return filepath

    def shot_ocr_processing(self):
        s = time.time() #print
        # 截图
        shot_path = self.shot()
        e = time.time()
        print(f'截图1：{e-s}')
        s = e
        # OCR
        text = self.ocr_engine.img_to_text(shot_path)
        e = time.time()
        print(f'截图2：{e-s}')
        s = e
        # OCR结果入队
        self.ocr_results.put(text)
        e = time.time()
        print(f'截图3：{e-s}')
        s = e
        # 图片使用后销毁
        print(f'已创建图片{shot_path.name}')
        shot_path.unlink()
        e = time.time()
        print(f'截图4：{e-s}')
        s = e

    def translate_processing(self, text: str):
        return self.translator.translate(text)
    
    def tts(self, text: str):
        self.player.generate_and_play_streaming(text)

    def start(self, x1, y1, x2, y2):
        '''
        入参是给pyautogui的截图坐标
        '''
        self.processing = True
        self.shot_position = (x1, y1, x2, y2)
        self.main_executor.submit(self.main_processing)

    def stop(self):
        self.processing = False
        self.player.stop()

    def main_processing(self):
        self.schedule_start()
        print('完成计划设定')
        while self.processing:
            # 如果ocr结果有东西就找翻译
            if not self.ocr_results.empty:
                ocr_text = self.ocr_results.get()
                print(f'ocr_text: {ocr_text}')
                # 判断ocr结果是否值得翻译
                if self.checker.check(ocr_text):
                    future = self.translate_executor.submit(self.translate_processing, ocr_text)
                    future.add_done_callback(lambda f: self.translate_results.put(f.result()))
                else:
                    pass
            # 如果翻译结果有东西就找TTS
            if not self.translate_results.empty:
                # 播放器未在运行才执行
                if self.tts_future is None or not self.tts_future.running():
                    trans_text = self.translate_results.get()
                    print(f'trans: {trans_text}')
                    self.tts_future = self.tts_executor.submit(self.tts, trans_text)

    def set_ocr_conf(self, exclude_set: set):
        self.ocr_engine.exclude_set = exclude_set
    
    def get_ocr_exclude_set(self) -> set:
        return self.ocr_engine.exclude_set
    
