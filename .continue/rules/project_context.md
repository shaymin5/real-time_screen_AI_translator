---
description: 项目上下文
---

# 项目上下文（PROJECT_CONTEXT）

## 项目目标
打造一个游戏实时翻译，识别屏幕内容，将需要翻译的文本翻译成中文后，用TTS模型播放声音。

## 项目性质
以学习为主、兼顾实用性的个人项目。

## 技术环境
- Python
- 本地开发环境

## 稳定设计取向
- 可维护性优先于极致性能
- 倾向使用直观、可理解的设计

## 异常处理
- 在需要捕获异常的地方捕获异常
- 除非功能必须，不做复杂的异常处理，用logging显示异常情况即可

## 技术栈
- GUI使用Tkinter
- pyautogui截图

## 已实现功能
- 名称: audio_process
    - 作用：多进程方式，接收text播放TTS语音
    - 文件：voxcpm_tts/tts/audio_process.py
- 名称：ocr
    - 作用：专为游戏优化的ocr模块
    - 文件：ocr.py
- 名称：translator
    - 作用：把文本翻译成中文
    - 文件：translator
- 名称：check
    - 作用：检查ocr识别出来的内容是否需要传递给translator翻译，内部已实现文本去重功能。
    - 文件：utils.py
- 名称：GUI
    - 作用：用户界面，用户在这里调整各种参数、开始和结束任务。这里可以获得格式为四个元素的tuple的需翻译屏幕范围。
    - 文件：gui.py

## 其他事实
- controller主循环在单独的线程中启动
