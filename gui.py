import tkinter as tk
from tkinter import ttk
import pickle
import threading
import logging

# 导入新的controller模块
try:
    from controller import GameTranslationController
except ImportError:
    # 如果controller模块不存在，创建一个简单的占位符
    logging.error("警告: controller模块未找到，请确保controller.py存在")
    raise ImportError()
    # 创建简单的占位符类
    # class GameTranslationController:
    #     def __init__(self, **kwargs):
    #         pass
    #     def start(self, region):
    #         print(f"Controller start called with region: {region}")
    #     def stop(self):
    #         print("Controller stop called")
    #     def get_ocr_exclude_set(self):
    #         return set()


class GameEyesApp:
    def __init__(self, root: tk.Tk):
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        
        # 加载配置
        self.config: dict = self.load_config()
        
        # 创建controller实例
        self.controller = None
        
        # translator的初始化参数，除外字符串集
        self.exclude_set: set = self.config['exclude_set']

        self.root = root
        self.root.title("游戏实时翻译器")
        self.root.geometry("600x500")  # 增加初始窗口大小
        self.root.resizable(True, True)  # 允许调整大小
        
        # 设置最小窗口大小，防止过小
        self.root.minsize(550, 450)
        
        # 加载截图区域坐标，默认全屏
        self.start_x: int = self.config.get('start_x', 0)
        self.start_y: int = self.config.get('start_y', 0)
        self.end_x: int = self.config.get('end_x', self.root.winfo_screenwidth())  # 最大x值
        self.end_y: int = self.config.get('end_y', self.root.winfo_screenheight())  # 最大y值
        
        # 截图控制变量
        self.is_selecting: bool = False
        self.is_capturing: bool = False
        self.interval: float = 0.4  # 截图时间间隔
        
        # 初始化界面变量
        # 定义支持的语言列表
        self.supported_languages = ['英语', '简体中文+英语', '日语', '繁体中文', '韩语', '法语', '德语', '西班牙语', '俄语']
        # 语言映射字典
        self.languages_mapping = {
            "英语": ["en"],
            "简体中文+英语": ['ch_sim','en'],
            "日语": ["ja"],
            "繁体中文": ["ch_tra"],
            "韩语": ["ko"],
            "法语": ["fr"],
            "德语": ["de"],
            "西班牙语": ["es"],
            "俄语": ["ru"]
        }
        self.source_lang_var: tk.StringVar = tk.StringVar(value=self.config.get('source_lang_var', '英语')) # 源语言变量
        self.use_gpu_ocr: tk.BooleanVar = tk.BooleanVar(value=self.config.get('use_gpu_ocr', True)) # GPU OCR变量

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
    # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮框架 - 始终显示
        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始/停止按钮
        self.start_button = ttk.Button(self.control_frame, text="开始翻译", command=self.start_capture)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(self.control_frame, text="停止翻译", command=self.stop_capture, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 折叠/展开按钮
        self.toggle_button = ttk.Button(self.control_frame, text="▼ 显示设置", command=self.toggle_settings)
        self.toggle_button.pack(side=tk.RIGHT)
        
        # 设置框架 - 初始状态为折叠
        self.settings_frame = ttk.LabelFrame(main_frame, text="翻译设置", padding="10")
        self.settings_visible = False  # 初始不显示设置
        
        # 区域选择部分
        area_frame = ttk.Frame(self.settings_frame)
        area_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(area_frame, text="1. 框选区域", command=self.start_area_selection).pack(side=tk.LEFT, padx=(0, 10))
        self.area_label = ttk.Label(area_frame, text=f"区域: ({self.start_x}, {self.start_y}) - ({self.end_x}, {self.end_y})")
        self.area_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 语言设置部分
        lang_frame = ttk.Frame(self.settings_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 源语言设置
        source_frame = ttk.LabelFrame(lang_frame, text="源语言", padding="5")
        source_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 创建源语言下拉菜单
        source_combo = ttk.Combobox(
            source_frame, 
            textvariable=self.source_lang_var,
            values=self.supported_languages,
            state="readonly",
            width=15
        )
        source_combo.pack(fill=tk.X, padx=5, pady=5)
        
        # GPU OCR设置
        gpu_frame = ttk.LabelFrame(lang_frame, text="OCR设置", padding="5")
        gpu_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建GPU OCR复选框
        gpu_check = ttk.Checkbutton(
            gpu_frame,
            text="启用GPU加速",
            variable=self.use_gpu_ocr,
            onvalue=True,
            offvalue=False
        )
        gpu_check.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加备注标签
        note_label = ttk.Label(
            gpu_frame,
            text="如果有Nvidia GPU建议开启",
            foreground="gray",
            font=("TkDefaultFont", 8)
        )
        note_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
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
        self.update_status("请框选翻译区域...")
        
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
    
    def cancel_selection(self, event):
        self.selection_window.destroy()
        self.root.deiconify()
        self.is_selecting = False
        self.update_status("区域选择已取消")
        
    def start_capture(self):
        """开始翻译流程"""
        # 更新UI状态
        self.is_capturing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # 保存配置
        self.save_config()

        # 隐藏设置区域
        self.hide_settings()
        
        self.update_status("实时翻译开始...")
        
        # 获取语言设置
        selected_lang = self.source_lang_var.get()
        ocr_languages = self.languages_mapping.get(selected_lang, ["en"])
        
        # 创建并启动controller
        try:
            # 如果已有controller在运行，先停止
            if self.controller is not None:
                self.controller.stop()
                self.controller = None
            
            # 创建新的controller
            self.controller = GameTranslationController(
                ocr_languages=ocr_languages,
                ocr_use_gpu=self.use_gpu_ocr.get(),
                ocr_exclude_set=self.exclude_set,
                capture_interval=self.interval,
                max_text_length=200
            )
            
            # 在单独的线程中启动controller，避免阻塞GUI
            def run_controller():
                try:
                    if self.controller is None:
                        self.update_status("错误: controller未初始化")
                        self.root.after(0, self._reset_buttons)
                        return
                    region = (self.start_x, self.start_y, self.end_x, self.end_y)
                    self.controller.start(region)
                except Exception as e:
                    self.update_status(f"启动翻译失败: {e}")
                    # 恢复按钮状态
                    self.root.after(0, self._reset_buttons)
            
            # 启动controller线程
            controller_thread = threading.Thread(target=run_controller, daemon=True)
            controller_thread.start()
            
            self.update_status(f"翻译已启动，区域: ({self.start_x}, {self.start_y}) - ({self.end_x}, {self.end_y})")
            self.update_status(f"OCR语言: {selected_lang}, GPU加速: {'启用' if self.use_gpu_ocr.get() else '禁用'}")
            
        except Exception as e:
            self.update_status(f"启动翻译时发生错误: {e}")
            self._reset_buttons()
    
    def stop_capture(self):
        """停止翻译流程"""
        self.is_capturing = False

        # 显示设置区域
        self.show_settings()
        
        # 停止controller
        if self.controller is not None:
            try:
                self.controller.stop()
                self.update_status("正在停止翻译...")
            except Exception as e:
                self.update_status(f"停止翻译时发生错误: {e}")
            finally:
                self.controller = None
        
        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.update_status("翻译已停止")
        
        # 保存OCR排除集
        if self.controller is not None:
            self.exclude_set = self.controller.get_ocr_exclude_set()
            self.save_config()
    
    def _reset_buttons(self):
        """重置按钮状态"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_capturing = False
    
    def update_status(self, message):
        """更新状态显示"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
    
    def save_config(self):
        """保存配置"""
        # 获取OCR排除集
        exclude_set = set()
        if self.controller is not None:
            exclude_set = self.controller.get_ocr_exclude_set()
        elif hasattr(self, 'exclude_set'):
            exclude_set = self.exclude_set
        
        config = {
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y,
            "source_lang_var": self.source_lang_var.get(),
            "use_gpu_ocr": self.use_gpu_ocr.get(),
            "exclude_set": exclude_set
        }
        self.config.update(config)
        try:
            with open("app_config.pk", "wb") as f:
                pickle.dump(self.config, f)
        except Exception as e:
            self.update_status(f"保存配置失败: {e}")
    
    def load_config(self) -> dict:
        """加载配置"""
        try:
            with open("app_config.pk", "rb") as f:
                config: dict = pickle.load(f)
                config.setdefault("source_lang_var", "英语")
                config.setdefault("use_gpu_ocr", True)
                config.setdefault("exclude_set", set())
        except Exception as e:
            self.update_status(f"加载配置失败，使用默认配置: {e}")
            config = {
                "source_lang_var": "英语",
                "use_gpu_ocr": True,
                "exclude_set": set()
            }
        return config
    
    def on_closing(self):
        """窗口关闭时的处理"""
        self.is_capturing = False
        
        # 停止controller
        if self.controller is not None:
            self.controller.stop()
        
        # 保存配置
        self.save_config()
        
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameEyesApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()