import time
from queue import Queue
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, Future
import threading

class Gui:
    def __init__(self) -> None:
        self.shot = Queue(maxsize=10)
        self.oct_result = Queue(maxsize=5)
        self.translated_text = Queue(maxsize=3)
        self.processing = False

        # 定时任务线程池
        self.schedule_executor = ThreadPoolExecutor(max_workers=1)
        self.schedule_interval = 3000 # 定时任务间隔：毫秒
        self.schedule_start_time = None # 定时任务开始时间

        self.root = tk.Tk()
        self.root.title("简化版 OCR-TTS")

        self.setup_ui()
        self.root.mainloop()

    def start_processing(self):
        self.processing = True
        self.schedule_task()  # ← 第一次调用，开始循环
    
    def stop_processing(self):
        self.processing = False


    def schedule_task(self): # 主程序线程
        if not self.processing:
            return
        
        self.schedule_start_time = time.perf_counter()  # 高精度计时开始⏱️
        # 性能计数器的精度：纳秒级（1秒=10亿纳秒）
        self.schedule_future = self.schedule_executor.submit(self.ocr)
        self.schedule_future.add_done_callback(lambda f: self._on_schedule_done())
    
    def _on_schedule_done(self):
        elapsed = time.perf_counter()
        delay = max(1, self.schedule_interval-elapsed)
        timer = threading.Timer(delay,self.schedule_task)
        timer.daemon = True
        timer.start()


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

    def ocr(self):
        # 模拟ocr
        time.sleep(1)
        print("搞什么飞机")

if __name__ == "__main__":
    g = Gui()
