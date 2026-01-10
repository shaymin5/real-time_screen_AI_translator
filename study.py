import tkinter as tk
import threading
import queue
import time

class SimpleOCRTTSApp:
    """简化版OCR-TTS应用，适合快速实现"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("简化版 OCR-TTS")
        
        # 状态
        self.processing = False
        self.audio_queue = queue.Queue(maxsize=5)
        self.ocr_queue = queue.Queue()
        
        # 设置GUI
        self.setup_ui()
        
        # 启动工作线程
        self.start_workers()
        
    def setup_ui(self):
        """设置简单界面"""
        # 开始/停止按钮
        self.btn = tk.Button(
            self.root, 
            text="开始", 
            command=self.toggle_processing,
            font=("Arial", 14),
            width=10
        )
        self.btn.pack(pady=20)
        
        # 状态标签
        self.status = tk.Label(
            self.root,
            text="就绪",
            font=("Arial", 10)
        )
        self.status.pack()
        
        # OCR结果显示
        self.text_area = tk.Text(
            self.root,
            height=15,
            width=50,
            state='disabled'
        )
        self.text_area.pack(padx=10, pady=10)
        
    def toggle_processing(self):
        """切换处理状态"""
        if not self.processing:
            self.start_processing()
        else:
            self.stop_processing()
    
    def start_processing(self):
        """开始处理"""
        self.processing = True
        self.btn.config(text="停止", bg="red")
        self.status.config(text="运行中...")
        
        # 启动处理线程
        self.process_thread = threading.Thread(
            target=self.process_loop,
            daemon=True
        )
        self.process_thread.start()
        
        # 启动音频播放线程
        self.audio_thread = threading.Thread(
            target=self.audio_playback_loop,
            daemon=True
        )
        self.audio_thread.start()
        
        # 启动定时任务（不阻塞GUI！）
        self.schedule_task()
    
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.btn.config(text="开始", bg="SystemButtonFace")
        self.status.config(text="已停止")
    
    def schedule_task(self):
        """定时任务调度"""
        if not self.processing:
            return
        
        start_time = time.perf_counter()
        
        # 这里执行您的0.1秒定时任务
        # 必须快速！不能阻塞！
        self.your_fixed_task_here()
        
        # 计算耗时并精确调度下一次
        elapsed = (time.perf_counter() - start_time) * 1000
        delay = max(1, 100 - int(elapsed))  # 维持100ms间隔
        
        self.root.after(delay, self.schedule_task)
    
    def your_fixed_task_here(self):
        """您的0.1秒定时任务"""
        # 示例：更新界面
        current = time.strftime("%H:%M:%S")
        self.status.config(text=f"最后执行: {current}")
        
        # 这里添加您的实际任务
        # 重要：这个函数必须在10ms内完成！
        # 如果任务耗时，需要放到工作线程
        
    def process_loop(self):
        """处理循环：OCR + TTS"""
        import random
        
        while self.processing:
            # 1. 执行OCR（模拟）
            ocr_start = time.perf_counter()
            text = self.perform_ocr()  # 替换为您的OCR代码
            ocr_time = (time.perf_counter() - ocr_start) * 1000
            
            if text:
                # 在GUI线程中更新显示
                self.root.after(0, self.update_display, text)
                
                # 2. 执行TTS合成（模拟）
                tts_start = time.perf_counter()
                audio_data = self.perform_tts(text)  # 替换为您的TTS代码
                tts_time = (time.perf_counter() - tts_start) * 1000
                
                # 3. 将音频放入队列
                try:
                    self.audio_queue.put(audio_data, timeout=0.1)
                except queue.Full:
                    # 队列满，丢弃最旧数据
                    try:
                        self.audio_queue.get_nowait()
                        self.audio_queue.put_nowait(audio_data)
                    except:
                        pass
                
                # 控制处理速度
                total_time = ocr_time + tts_time
                if total_time < 100:  # 如果处理太快，稍微等待
                    time.sleep((100 - total_time) / 1000)
    
    def perform_ocr(self):
        """执行OCR（替换为您的OCR代码）"""
        # 模拟OCR处理
        time.sleep(0.05)  # 50ms OCR处理
        
        # 返回模拟文本
        texts = [
            "这是一段识别出的文本。",
            "Hello, world!",
            "OCR结果示例。",
            "实时文字识别。"
        ]
        return random.choice(texts)
    
    def perform_tts(self, text):
        """执行TTS合成（替换为您的TTS代码）"""
        # 模拟TTS处理
        time.sleep(0.03)  # 30ms TTS处理
        
        # 返回模拟音频数据
        return f"音频:{text}"
    
    def audio_playback_loop(self):
        """音频播放循环"""
        while self.processing:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                # 播放音频（替换为您的播放代码）
                self.play_audio(audio_data)
            except queue.Empty:
                continue
    
    def play_audio(self, audio_data):
        """播放音频（替换为您的播放代码）"""
        # 模拟播放
        time.sleep(0.1)  # 100ms播放时间
        print(f"播放: {audio_data}")
    
    def update_display(self, text):
        """更新显示"""
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')
        
        # 限制行数
        if int(self.text_area.index('end-1c').split('.')[0]) > 50:
            self.text_area.delete(1.0, 2.0)
    
    def start_workers(self):
        """启动工作线程"""
        # 可以在这里启动其他工作线程
        pass
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

# 快速启动
if __name__ == "__main__":
    app = SimpleOCRTTSApp()
    app.run()