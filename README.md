
<div align="center">

# 实时屏幕AI翻译工具 | Real-time Screen AI Translator Tool
中文 | [English](README_EN.md)

</div>

## 简介
这是一个用于将屏幕内容实时翻译成其他语言的Python应用程序。它使用本地OCR（光学字符识别）从选定的屏幕区域提取文本，然后使用在线AI翻译成中文。
## 功能特点
- **实时截图**：捕获屏幕并生成截图。
- **OCR识别**：从截图中提取文字。
## 快速开始
1. 安装uv来管理Python虚拟环境。[下载uv](https://github.com/astral-sh/uv)。
2. 克隆此仓库到本地并进入项目目录，或直接下载仓库
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```
3. 在目录下创建一个`.env`文件，在其中添加你的Deepseek API密钥
```text
DEEPSEEK_API_KEY=你的api密钥
```
4. 用`uv`安装依赖
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
- 目前仅支持英文翻译中文，后续考虑增加语言可选项。
- 未测试过cpu版的torch，有朋友感兴趣可以帮忙测下性能差异。RTX5060 8G显卡目前一般的图像OCR识别速度在0.1秒左右。

## 下一步计划
0. 搭建测试框架便于测试新features
1. 增加新语言支持
2. 开放API接口提示词修改功能，允许玩家自定义翻译服务
3. 增加ttf功能自动朗读（挑战）
   1. 发掘或制作简单易用的ttf音色训练方案
   2. 用户自练音色实装
4. 优化和新增OCR引擎支持，让硬件条件不好的玩家也可以露出笑容
5. 新增其他厂商的API接口
6. 对网络错误、API配额耗尽等异常情况做容错处理
7. 尝试实现常驻系统托盘，按快捷键唤起（可以先实现鼠标操作的快捷启动）
8. 尝试双屏方案
9. 优化运行环境自定义选项，玩家可以更方便选择torch版本