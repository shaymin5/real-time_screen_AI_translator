import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import threading
from datetime import datetime
import os
import json

from pathlib import Path
from ocr import OCR
from translate import Translator
from concurrent.futures import ThreadPoolExecutor

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("定时截图器")
        self.root.geometry("600x500")  # 增加初始窗口大小
        self.root.resizable(True, True)  # 允许调整大小
        
        # 设置最小窗口大小，防止过小
        self.root.minsize(550, 450)
        
        # 截图区域坐标
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        # 截图控制变量
        self.is_selecting = False
        self.is_capturing = False
        self.capture_thread = None
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()

        # 队列初始化
        self.image_queue = None
        self.text_queue = TextQueue2()
        # 翻译官初始化
        self.translator = None
        # 创建线程池
        self.executor = ThreadPoolExecutor(max_workers=1)
        # 跟踪当前翻译任务
        self.current_translation_future = None
        # 创建OCR对象
        self.ocr = OCR(languages=['en'])

    def create_widgets(self):
    # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮框架 - 始终显示
        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始/停止按钮
        self.start_button = ttk.Button(self.control_frame, text="开始截图", command=self.start_capture)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(self.control_frame, text="停止截图", command=self.stop_capture, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 折叠/展开按钮
        self.toggle_button = ttk.Button(self.control_frame, text="▼ 显示设置", command=self.toggle_settings)
        self.toggle_button.pack(side=tk.RIGHT)
        
        # 设置框架 - 初始状态为折叠
        self.settings_frame = ttk.LabelFrame(main_frame, text="截图设置", padding="10")
        self.settings_visible = False  # 初始不显示设置
        
        # 区域选择部分
        area_frame = ttk.Frame(self.settings_frame)
        area_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(area_frame, text="1. 框选区域", command=self.start_area_selection).pack(side=tk.LEFT, padx=(0, 10))
        self.area_label = ttk.Label(area_frame, text="未选择区域")
        self.area_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 定时设置部分
        timer_frame = ttk.Frame(self.settings_frame)
        timer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用Frame来组织定时设置的布局
        timer_subframe = ttk.Frame(timer_frame)
        timer_subframe.pack(fill=tk.X)
        
        ttk.Label(timer_subframe, text="截图间隔(秒):").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value="0.4")  # 根据您的图片设置为0.4秒
        interval_entry = ttk.Entry(timer_subframe, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(timer_subframe, text="截图次数(0=无限):").grid(row=0, column=2, sticky=tk.W)
        self.count_var = tk.StringVar(value="0")
        count_entry = ttk.Entry(timer_subframe, textvariable=self.count_var, width=10)
        count_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # 配置定时设置子框架的列权重
        timer_subframe.columnconfigure(1, weight=1)
        timer_subframe.columnconfigure(3, weight=1)
        
        # 保存设置部分
        save_frame = ttk.Frame(self.settings_frame)
        save_frame.pack(fill=tk.X)
        
        # 保存路径行
        path_frame = ttk.Frame(save_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_frame, text="保存路径:", width=10).pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), "temp_screenshots"))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(path_frame, text="浏览", command=self.browse_path).pack(side=tk.LEFT)
        
        # 文件名前缀行
        prefix_frame = ttk.Frame(save_frame)
        prefix_frame.pack(fill=tk.X)
        
        ttk.Label(prefix_frame, text="文件名前缀:", width=10).pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar(value="temp_screenshot")
        prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var)
        prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 状态显示 - 使用pack并允许扩展
        self.status_frame = ttk.LabelFrame(main_frame, text="状态", padding="10")
        self.status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态文本框和滚动条
        text_scroll_frame = ttk.Frame(self.status_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(text_scroll_frame, wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # 初始状态：不显示设置区域
        self.hide_settings()

    def toggle_settings(self):
        """切换设置区域的显示/隐藏"""
        if self.settings_visible:
            self.hide_settings()
        else:
            self.show_settings()

    def hide_settings(self):
        """隐藏设置区域"""
        if hasattr(self, 'settings_frame') and self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
        self.settings_visible = False
        self.toggle_button.config(text="▼ 显示设置")
        
    def show_settings(self):
        """显示设置区域"""
        if hasattr(self, 'settings_frame') and not self.settings_frame.winfo_ismapped():
            self.settings_frame.pack(fill=tk.X, pady=(0, 10), before=self.status_frame)
        self.settings_visible = True
        self.toggle_button.config(text="▲ 隐藏设置")

    def start_area_selection(self):
        self.is_selecting = True
        self.update_status("请框选截图区域...")
        
        # 最小化主窗口
        self.root.iconify()
        
        # 创建全屏透明窗口用于区域选择
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.configure(background='black')
        
        # 绑定鼠标事件
        self.selection_window.bind('<Button-1>', self.on_selection_start)
        self.selection_window.bind('<B1-Motion>', self.on_selection_drag)
        self.selection_window.bind('<ButtonRelease-1>', self.on_selection_end)
        
        # 绑定退出键
        self.selection_window.bind('<Escape>', self.cancel_selection)
        
        # 设置窗口在最前
        self.selection_window.attributes('-topmost', True)
    
    def on_selection_start(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        # 创建选择矩形
        self.selection_rect = tk.Frame(self.selection_window, background='red', borderwidth=1)
        self.selection_rect.place(x=self.start_x, y=self.start_y, width=1, height=1)
    
    def on_selection_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            # 更新选择矩形
            x = min(self.start_x, event.x)
            y = min(self.start_y, event.y)
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            
            self.selection_rect.place(x=x, y=y, width=width, height=height)
    
    def on_selection_end(self, event):
        self.end_x = event.x
        self.end_y = event.y
        
        # 确保坐标正确（左上角和右下角）
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        self.area_label.config(text=f"区域: ({x1}, {y1}) - ({x2}, {y2})")
        self.update_status(f"区域选择完成: ({x1}, {y1}) 到 ({x2}, {y2})")
        
        # 关闭选择窗口
        self.selection_window.destroy()
        self.root.deiconify()  # 恢复主窗口
        self.is_selecting = False
        
        # 保存配置
        self.save_config()
    
    def cancel_selection(self, event=None):
        self.selection_window.destroy()
        self.root.deiconify()
        self.is_selecting = False
        self.update_status("区域选择已取消")
    
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            self.save_config()
    
    def start_capture(self):
        # 验证输入
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError("间隔时间必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的间隔时间（大于0的数字）")
            return
        
        try:
            count = int(self.count_var.get())
            if count < 0:
                raise ValueError("截图次数不能为负数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的截图次数（非负整数）")
            return
        
        if self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None:
            messagebox.showerror("错误", "请先选择截图区域")
            return
        
        # 确保保存目录存在
        save_path = self.path_var.get()
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except OSError as e:
                messagebox.showerror("错误", f"无法创建保存目录: {e}")
                return
        
        # 更新UI状态
        self.is_capturing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 初始化图片队列
        self.image_queue = ImageQueue2(Path(self.path_var.get()), size=20)

        # 初始化OCR
        self.ocr = OCR(languages=['en'])

        # 初始化翻译官
        self.translator = Translator()

        # 隐藏设置区域
        self.hide_settings()
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.update_status("开始定时截图...")

        # 启动截图线程
        self.capture_thread = threading.Thread(
            target=self.capture_loop, 
            args=(interval, count),
            daemon=True
        )
        self.capture_thread.start()
    
    def stop_capture(self):
        self.is_capturing = False

         # 显示设置区域
        self.show_settings()
        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.update_status("截图已停止")    
    
    def capture_loop(self, interval, count):
        captured_count = 0
        
        start_time = time.time()
        while self.is_capturing:
            # 计算截图区域
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            width = x2 - x1
            height = y2 - y1
            
            # 截图
            try:
                screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"{self.prefix_var.get()}_{timestamp}.png"
                filepath = os.path.join(self.path_var.get(), filename)
                
                # 保存图片
                screenshot.save(filepath)
                # 更新队列
                self.image_queue.put(filepath)

                # 进行OCR识别 todo
                ocr_result = self.ocr.ocr_image(filepath)
                if self.text_queue.compare(ocr_result):
                    # 检查是否有正在进行的翻译任务
                    if self.current_translation_future is None or self.current_translation_future.done():
                        # 没有正在进行的翻译任务，提交新的翻译任务
                        future = self.executor.submit(self.translator.translate, ocr_result)
                        self.current_translation_future = future
                        
                        # 设置回调函数，翻译完成后在主线程更新UI
                        def on_translation_done(future):
                            try:
                                text = future.result()
                                if text:
                                    self.root.after(0, self.update_status, f"\n{text}")
                            except Exception as e:
                                print(f"翻译失败: {e}")
                            finally:
                                # 任务完成后清理引用
                                if self.current_translation_future == future:
                                    self.current_translation_future = None
                        
                        future.add_done_callback(on_translation_done)
                    else:
                        # 有翻译任务正在进行，跳过本次翻译
                        # print("跳过翻译：上一个翻译任务尚未完成")
                        pass

                # 检查是否达到指定次数 上面pass时这里会有bug，但无所谓
                captured_count += 1
                if count > 0 and captured_count >= count:
                    self.root.after(0, self.stop_capture)
                    break
                    
            except Exception as e:
                self.root.after(0, self.update_status, f"截图失败: {str(e)}")
            
            # 等待指定间隔
            for _ in range(int(interval * 10)):
                if not self.is_capturing:
                    break
                if start_time + interval <= time.time():
                    start_time = time.time()
                    break
                time.sleep(0.1)
            else:
                start_time = time.time()
    
    def update_status(self, message):
        # timestamp = datetime.now().strftime("%H:%M:%S")
        # self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
    
    def save_config(self):
        config = {
            "interval": self.interval_var.get(),
            "count": self.count_var.get(),
            "path": self.path_var.get(),
            "prefix": self.prefix_var.get(),
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y
        }
        
        try:
            with open("screenshot_config.json", "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        try:
            with open("screenshot_config.json", "r") as f:
                config = json.load(f)
                
            self.interval_var.set(config.get("interval", "5"))
            self.count_var.set(config.get("count", "0"))
            self.path_var.set(config.get("path", os.path.join(os.getcwd(), "temp_screenshots")))
            self.prefix_var.set(config.get("prefix", "temp_screenshot"))
            
            self.start_x = config.get("start_x")
            self.start_y = config.get("start_y")
            self.end_x = config.get("end_x")
            self.end_y = config.get("end_y")
            
            if all(v is not None for v in [self.start_x, self.start_y, self.end_x, self.end_y]):
                x1 = min(self.start_x, self.end_x)
                y1 = min(self.start_y, self.end_y)
                x2 = max(self.start_x, self.end_x)
                y2 = max(self.start_y, self.end_y)
                self.area_label.config(text=f"区域: ({x1}, {y1}) - ({x2}, {y2})")
                
        except FileNotFoundError:
            pass  # 配置文件不存在，使用默认值
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def on_closing(self):
        self.is_capturing = False
        self.save_config()
        self.root.destroy()


class TextQueue2:
    def __init__(self, size=2):
        self.items:list[str] = []
        self.size = size
    
    def compare(self,item:str):
        # queue 未满时，直接添加
        if len(self.items) < self.size:
            self.items.append(item)
            return False
        # queue 已满时，弹出最早的，添加新的，比较最后两个
        elif len(self.items) >= self.size:
            self.items.pop(0)
            self.items.append(item)
            return self.items[-2] == self.items[-1]
        return False
    
    def get(self):
        if len(self.items) >= 2:
            return self.items[-1]


class ImageQueue2:
    def __init__(self, parent_path: Path,size=5):
        self.items = []
        self.parent_path = parent_path
        self.size = size

        for png_file in self.parent_path.glob("*.png"):
            png_file.unlink()  # 删除文件
    
    def put(self, item):
        item = Path(item)
        if len(self.items) >= self.size:
            unlink = self.items.pop(0)
            unlink.unlink()  # 删除文件
        self.items.append(item)
    
    def get(self):
        if not self.is_empty() and len(self.items) >= 2:
            return self.items[-2], self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
if __name__ == "__main__":
    
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()