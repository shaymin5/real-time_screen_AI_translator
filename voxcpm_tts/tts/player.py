import numpy as np
import pyaudio
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from voxcpm import VoxCPM

class SyncBufferedTTSPlayer:
    """完全同步的预缓冲播放器，避免异步问题"""
    
    def __init__(self, model:VoxCPM, buffer_seconds=0.3):
        self.model = model
        self.sample_rate = model.tts_model.sample_rate
        self.buffer_seconds = buffer_seconds
        self.buffer_size = int(buffer_seconds * self.sample_rate)
        
        # 音频设备
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # 控制
        self.is_playing = False
        self.stop_event = threading.Event()
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def _generate_to_queue(self, audio_queue, kwargs):
        """生成音频到队列"""
        print("开始生成音频: '...'")
        
        try:
            for chunk in self.model.generate_streaming(**kwargs):
                if self.stop_event.is_set():
                    break
                
                if len(chunk) > 0:
                    audio_queue.put(chunk)
            
            audio_queue.put(None)  # 结束标记
            
        except Exception as e:
            print(f"生成音频失败: {e}")
            audio_queue.put(None)
    
    def _play_from_queue(self, audio_queue):
        """从队列播放音频"""
        print("开始播放...")
        
        # 初始化音频流
        if not self.stream:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=2048
            )
        
        # 第一阶段：收集预缓冲
        buffer = []
        buffered_samples = 0
        
        while (buffered_samples < self.buffer_size and 
               not self.stop_event.is_set() and
               not (audio_queue.empty() and audio_queue.qsize() == 0)):
            
            try:
                chunk = audio_queue.get(timeout=0.1)
                if chunk is None:  # 提前结束
                    break
                
                buffer.append(chunk)
                buffered_samples += len(chunk)
                
            except queue.Empty:
                # 如果没有数据但生成线程还在运行，继续等待
                continue
        
        print(f"预缓冲完成: {buffered_samples/self.sample_rate:.2f}秒")
        
        # 播放缓冲的数据
        for chunk in buffer:
            if self.stop_event.is_set():
                break
            
            if chunk.dtype != np.float32:
                chunk = chunk.astype(np.float32)
            self.stream.write(chunk.tobytes())
        
        # 第二阶段：继续播放队列中的数据
        while not self.stop_event.is_set():
            try:
                chunk = audio_queue.get(timeout=0.1)
                
                if chunk is None:  # 结束标记
                    break
                
                if chunk.dtype != np.float32:
                    chunk = chunk.astype(np.float32)
                self.stream.write(chunk.tobytes())
                
            except queue.Empty:
                # 检查生成线程是否还在运行
                if not self.is_generating:
                    break
                continue
        
        print("播放完成")
    
    def play_streaming(self, generate_conf:dict, buffer_seconds:float=0.5):
        self.buffer_size = int(buffer_seconds * self.sample_rate)
        """播放TTS音频"""
        if self.is_playing:
            print("已经在播放中，先停止当前播放")
            self.stop()
            time.sleep(0.1)
        
        # 重置状态
        self.is_playing = True
        self.stop_event.clear()
        
        # 创建队列
        audio_queue = queue.Queue(maxsize=50)
        
        # 启动生成线程
        self.is_generating = True
        
        def generation_wrapper():
            try:
                self._generate_to_queue(audio_queue, generate_conf)
            finally:
                self.is_generating = False
        
        gen_thread = threading.Thread(target=generation_wrapper, daemon=True)
        gen_thread.start()
        
        # 在主线程中播放（避免线程间同步问题）
        self._play_from_queue(audio_queue)
        
        # 等待生成线程结束
        gen_thread.join(timeout=2.0)
        
        # 更新状态
        self.is_playing = False
    
    def stop(self):
        """停止播放"""
        self.stop_event.set()
        self.is_playing = False
    
    def cleanup(self):
        """清理资源"""
        self.stop()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.p.terminate()

# 使用示例
# if __name__ == "__main__":
#     player = SyncBufferedTTSPlayer(
#         sample_rate=24000,
#         buffer_seconds=0.5
#     )
    
#     try:
#         # 播放音频
#         player.play_streaming(
#             text="这是一个流式TTS播放的示例，使用了预缓冲技术来避免卡顿。",
#             model=tts_model
#         )
        
#         # 可以多次播放
#         time.sleep(1)
#         player.play_streaming(
#             text="这是第二次播放，同样会使用预缓冲。",
#             model=tts_model
#         )
        
#     except KeyboardInterrupt:
#         print("\n用户中断")
#     except Exception as e:
#         print(f"错误: {e}")
#     finally:
#         player.cleanup()