
<div align="center">

# 实时屏幕AI翻译工具 | Real-time Screen AI Translator Tool
中文 | [英文](README_EN.md)

</div>

## 简介
这是一个用于将屏幕内容实时翻译成其他语言的Python应用程序。它使用本地OCR（光学字符识别）从选定的屏幕区域提取文本，然后使用在线AI翻译成中文。
## 功能特点
- **实时截图**：捕获屏幕并生成截图。
- **OCR识别**：从截图中提取文字。
## 快速开始
1. 安装uv来管理Python虚拟环境。[下载uv](https://github.com/astral-sh/uv)
2. 克隆此仓库到本地并进入项目目录：
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```
3. 在目录下创建一个`.env`文件，在其中添加你的Deepseek API密钥
```text
DEEPSEEK_API_KEY=你的api密钥
```
4. 用uv安装依赖
```bash
uv sync
```
安装torch时因为在国外服务器下载，速度慢正常，使用代理可以提速。目前该操作默认下载torch的cu128即gpu版本，没有Nvida显卡请下载cpu版本。下载cpu版本请把`pyproject.toml`中的
`https://download.pytorch.org/whl/cu128`替换为`https://download.pytorch.org/whl/cpu`或`https://pypi.tuna.tsinghua.edu.cn/simple`，后者在中国大陆下载速度较快。
如果你的设备对torch版本有要求，请自行修改`https://download.pytorch.org/whl/cu128`为相应地址。
5. 开始运行
```bash
uv run main.py
```
## 提示
- 目前的版本建议只框选翻译范围，不要改动其他设置。
- 暂只支持Deepseek API，性价比之选。后续考虑接入翻译速度更快的AI。