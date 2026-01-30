<div align="center">

# 实时屏幕AI翻译工具 | Real-time Screen AI Translator Tool

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white) · ![uv](https://img.shields.io/badge/uv-1.x-orange) · ![TTS](https://img.shields.io/badge/TTS-VoxCpm-green) · ![AI](https://img.shields.io/badge/AI-DeepSeek-6c47ff)

</div>

## 目录
- [简介](#简介)
- [功能特点](#功能特点)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [性能说明](#性能说明)
- [常见问题](#常见问题)
- [开发计划](#开发计划)

## 简介
这是一个用于将屏幕内容实时翻译成其他语言的Python应用程序。它使用本地OCR（光学字符识别）从选定的屏幕区域提取文本，然后使用在线AI翻译成中文，并支持TTS语音播报和智能游戏UI屏蔽。

## 功能特点
- **实时截图**：捕获屏幕并生成截图。
- **OCR识别**：从截图中提取文字。
- **在线翻译**：使用Deepseek API进行高质量翻译。
- **自动屏蔽游戏UI**：自动识别并屏蔽游戏界面元素，v2.0优化后识别更精准、提取更流畅。
- **TTS语音播报**：基于VoxCpm的语音合成，实时朗读翻译结果，解放双眼。

## 系统要求
- **Python**: 3.11
- **操作系统**: Windows 10/11
- **存储空间**: 至少5GB可用空间（用于模型文件）
- **内存**: 建议8GB以上
- **显存**: 6GB以上
- **网络连接**: 需要访问Deepseek API

## 快速开始

### 1. 安装前置工具
安装uv来管理Python虚拟环境：[下载uv](https://github.com/astral-sh/uv)

### 2. 获取项目代码
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```

### 3. 配置API密钥
获取[DeepSeek API密钥](https://platform.deepseek.com/usage)
在项目根目录创建`.env`文件，添加你的Deepseek API密钥：
```text
DEEPSEEK_API_KEY=你的api密钥
```

### 4. 下载TTS模型（用于语音播报）
在魔塔社区[下载TTS模型](https://modelscope.cn/models/Shaymin726/haibara_lora/summary)，解压后放在`voxcpm_tts/model/`目录下。

目录结构应如下所示：
```
├── voxcpm_tts/                  # TTS语音合成模块
│   ├── model/                   # TTS模型文件
│   │   ├── lora/               # LoRA模型文件
│   │   ├── prompt/             # 提示词文件
│   │   └── voxcpm_pretrained/  # 预训练模型
```

### 5. 安装依赖
```bash
uv init
uv sync
```

### 6. 运行程序
```bash
uv run main.py
```

## 使用指南
1. 启动程序后会出现GUI界面
2. 选择要翻译的屏幕区域
3. 配置翻译选项
4. 点击"开始"按钮开始实时翻译
5. 翻译结果会以语音形式播报

## 性能说明
- **首次使用**：需要下载OCR模型，请保持网络连接
- **翻译服务**：依赖Deepseek API，需要稳定的网络连接

## 常见问题

### Q: 安装torch时速度很慢怎么办？
A: 可以尝试以下方法：
1. 使用代理加速下载
2. 修改`pyproject.toml`中的PyTorch源地址：
   - CPU版本：替换为`https://download.pytorch.org/whl/cpu`
   - 中国大陆用户：替换为`https://pypi.tuna.tsinghua.edu.cn/simple`
   - 有NVIDIA显卡：保持默认的`https://download.pytorch.org/whl/cu128`

### Q: 支持哪些语言？
A: 目前主要支持英文翻译中文，后续会支持更多语言。

### Q: 可以离线使用吗？
A: OCR和TTS可以本地运行，但翻译需要网络连接访问Deepseek API。

### Q: 第一次使用为什么很慢？
A: 首次使用需要下载OCR模型和TTS模型，后续使用会快很多。

## 开发计划
- [ ] 支持更多翻译API
- [ ] 增加更多语言选项
- [ ] 优化OCR性能
- [ ] 添加更多TTS语音选项

---

**提示**：
- 本工具主要支持英文翻译中文，适用窗口游戏场景
- Deepseek API是目前性价比较高的选择，后续会考虑接入更多翻译服务
- 项目以实用性为主，兼顾学习用途，欢迎提出改进建议