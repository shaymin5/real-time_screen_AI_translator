# controller.py
import pyautogui
import logging
import time
import multiprocessing as mp
from typing import Tuple, Optional, List
import numpy as np

from ocr import GameOCR
from translator import Translator
from voxcpm_tts.tts.audio_process import audio_process_entry

logger = logging.getLogger(__name__)


class GameTranslationController:
    """
    游戏实时翻译控制器
    负责协调截图、OCR、翻译、TTS播放的整体流程
    """
    
    def __init__(
        self,
        ocr_languages: List[str] | None = None,
        ocr_use_gpu: bool = True,
        ocr_exclude_set: Optional[set] = None,
        capture_interval: float = 0.8,
        max_text_length: int = 200,
        similarity_threshold: float = 0.8
    ):
        """
        初始化控制器
        
        Args:
            ocr_languages: OCR支持的语言列表，默认['en']
            ocr_use_gpu: 是否使用GPU加速OCR
            ocr_exclude_set: OCR排除的字符串集合
            capture_interval: 截图间隔（秒）
            max_text_length: 最大文本长度限制
            similarity_threshold: 文本相似度阈值
        """
        # 默认参数
        if ocr_languages is None:
            ocr_languages = ['en']
    
        self.capture_interval = capture_interval
        self.max_text_length = max_text_length
        self.running = False
        self.initialized = False  # 新增：初始化状态标志
        
        # 初始化OCR模块
        self.ocr = GameOCR(
            languages=ocr_languages,
            gpu=ocr_use_gpu,
            exclude_set=ocr_exclude_set
        )
        
        # 初始化翻译模块（内部已集成Checker）
        self.translator = Translator()
        
        # 初始化音频进程
        self.audio_cmd_queue = mp.Queue()
        self.audio_process = mp.Process(
            target=audio_process_entry,
            args=(self.audio_cmd_queue,),
            daemon=True
        )
        
        # 立即启动音频进程（新增）
        self.audio_process.start()
        logger.info("音频进程已启动（预加载TTS模型）")
        
        # 截图区域
        self.capture_region: Optional[Tuple[int, int, int, int]] = None
        
        self.initialized = True  # 标记为已初始化
        logger.info("游戏翻译控制器初始化完成（音频进程已启动）")
    
    def set_capture_region(self, region: Tuple[int, int, int, int]):
        """
        设置截图区域
        
        Args:
            region: (x1, y1, x2, y2) 左上角和右下角坐标
        """
        x1, y1, x2, y2 = region
        # 确保坐标正确
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.capture_region = (x1, y1, x2, y2)
        logger.info(f"设置截图区域: {self.capture_region}")
    
    def start(self, region: Tuple[int, int, int, int]):
        """
        开始翻译流程
        
        Args:
            region: (x1, y1, x2, y2) 截图区域
        """
        if self.running:
            logger.warning("翻译流程已经在运行中")
            return
        
        if not self.initialized:
            logger.error("控制器未正确初始化")
            return
        
        # 设置截图区域
        self.set_capture_region(region)
        
        # 不再需要启动音频进程，因为已经在__init__中启动了
        # 设置运行标志
        self.running = True
        
        # 在主线程中运行主循环（避免阻塞GUI）
        # 注意：在实际使用中，这个循环应该在单独的线程中运行
        self._run_main_loop()
    
    def stop(self):
        """停止翻译流程"""
        if not self.running:
            logger.warning("翻译流程未在运行")
            return
        
        self.running = False
        logger.info("正在停止翻译流程...")
        
        # 不再停止音频进程，只停止主循环
        # 保存OCR排除集
        self._save_ocr_exclude_set()
        
        logger.info("翻译流程已停止（音频进程保持运行）")

    def shutdown(self):
        """完全关闭控制器，包括音频进程"""
        # 先停止主循环
        if self.running:
            self.stop()
        
        # 停止音频进程
        self._stop_audio_process()
        
        logger.info("控制器已完全关闭")
    
    def _run_main_loop(self):
        """运行主循环"""
        logger.info("开始翻译主循环")
        
        try:
            while self.running:
                # 执行一个处理周期
                self._process_cycle()
                
                # 等待下一个周期
                time.sleep(self.capture_interval)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号")
            self.stop()
        except Exception as e:
            logger.error(f"主循环发生错误: {e}", exc_info=True)
            self.stop()
    
    def _process_cycle(self):
        """单个处理周期：截图→OCR→翻译→TTS"""
        try:
            # 1. 截图
            screenshot = self._capture_screen()
            if screenshot is None:
                return
            
            # 2. OCR识别
            ocr_text = self._perform_ocr(screenshot)
            if not ocr_text:
                return
            
            # 3. 翻译（内部已包含Checker检查）
            translated_text = self._perform_translation(ocr_text)
            if not translated_text:
                return
            
            # 4. TTS播放
            self._speak_text(translated_text)
            
        except Exception as e:
            logger.error(f"处理周期发生错误: {e}", exc_info=True)
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """截图并返回numpy数组"""
        try:
            if self.capture_region is None:
                logger.error("未设置截图区域")
                return None
            
            # 将 (x1, y1, x2, y2) 格式转换为 (x, y, width, height) 格式
            x1, y1, x2, y2 = self.capture_region
            x = x1
            y = y1
            width = x2 - x1
            height = y2 - y1
            
            # 确保宽度和高度为正数
            if width <= 0 or height <= 0:
                logger.error(f"无效的截图区域: {self.capture_region}")
                return None
            
            # 使用pyautogui截图（需要width, height格式）
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # 转换为numpy数组（OpenCV格式）
            img_array = np.array(screenshot)
            # 转换颜色空间 BGR -> RGB
            img_array = img_array[:, :, ::-1].copy()
            
            logger.debug(f"截图成功: 区域({x1}, {y1}, {x2}, {y2}) -> ({x}, {y}, {width}, {height})")
            return img_array
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def _perform_ocr(self, image: np.ndarray) -> str:
        """执行OCR识别"""
        # try:
        #     text = self.ocr.img_to_text(image)
        #     if text:
        #         logger.debug(f"OCR识别结果: {text[:50]}...")  # 只显示前50个字符
        #     return text
        # except Exception as e:
        #     logger.error(f"OCR识别失败: {e}")
        #     return ""
        try:
            text = self.ocr.img_to_text(image)
            if text:
                logger.debug(f"OCR识别结果: {text[:50]}...")  # 只显示前50个字符
                # 添加控制台输出
                print(f"[OCR原始文本] {text}")
            return text
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return ""
    
    def _perform_translation(self, text: str) -> str:
        """执行翻译"""
        try:
            # Translator内部已经集成了Checker
            translated_text = self.translator.translate(text)
            if translated_text:
                logger.debug(f"翻译结果: {translated_text[:50]}...")  # 只显示前50个字符
            return translated_text
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return ""
    
    def _speak_text(self, text: str):
        """通过TTS播放文本"""
        try:
            # 限制文本长度
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length] + "..."
            
            # 发送语音命令
            self.audio_cmd_queue.put({
                "type": "speak",
                "text": text
            })
            logger.debug(f"发送TTS命令: {text[:30]}...")
            
        except Exception as e:
            logger.error(f"发送TTS命令失败: {e}")
    
    def _stop_audio_process(self):
        """停止音频进程"""
        try:
            if self.audio_process.is_alive():
                self.audio_cmd_queue.put({"type": "exit"})
                self.audio_process.join(timeout=5)
                if self.audio_process.is_alive():
                    self.audio_process.terminate()
                logger.info("音频进程已停止")
        except Exception as e:
            logger.error(f"停止音频进程失败: {e}")
    
    def _save_ocr_exclude_set(self):
        """保存OCR排除集"""
        try:
            self.ocr.save_exclude_set()
            logger.info("OCR排除集已保存")
        except Exception as e:
            logger.error(f"保存OCR排除集失败: {e}")
    
    def get_ocr_exclude_set(self) -> set:
        """获取OCR排除集"""
        return self.ocr.exclude_set
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.running


# 简单的测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # 创建控制器
    controller = GameTranslationController(
        ocr_languages=['en'],
        ocr_use_gpu=True,
        capture_interval=1.0  # 测试时使用较长的间隔
    )
    
    try:
        # 开始翻译（示例区域：屏幕左上角800x600区域）
        print("开始翻译测试...")
        print("按Ctrl+C停止")
        controller.start((0, 0, 800, 600))
        
        # 等待用户中断
        while controller.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止...")
        controller.stop()