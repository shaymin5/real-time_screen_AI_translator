
<div align="center">

# 实时屏幕AI翻译工具 | Real-time Screen AI Translator Tool
中文 | [English](README_EN.md)

</div>

## 简介
这是一个用于将屏幕内容实时翻译成其他语言的Python应用程序。它使用本地OCR（光学字符识别）从选定的屏幕区域提取文本，然后使用在线AI翻译成中文。
## 功能特点
- **实时截图**：捕获屏幕并生成截图。
- **OCR识别**：从截图中提取文字。
- **在线翻译**：用deepseek的api进行翻译。
- **自动屏蔽游戏UI**：自动识别并屏蔽游戏界面元素。
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
- 第一次选择某种源语言时需要等待下载OCR模型。后续无需下载，速度会快很多。
- 暂只支持Deepseek API，性价比之选。后续考虑接入翻译速度更快的AI。
- 目前仅支持英文翻译中文，后续考虑增加语言可选项。
- OCR识别速度性能差异：RTX5060 8G 在0.1秒左右，造成延迟0.2秒；锐龙9500f在0.3秒左右，造成延迟0.6秒。
## 注意
本项目使用到`pickle`模块加载`.pk`文件，项目本身不携带该文件，该文件在运行过程中产生，仅用于保存设置和屏蔽词库。请勿信任来源不明的`.pk`文件，恶意的`.pk`文件可能会使你的电脑遭受安全威胁。

## 下一步计划
- [ ] 异步翻译，提升体验
- [x] 增加新语言支持
- [ ]  开放API接口提示词修改功能，允许玩家自定义翻译服务
- [ ]  增加ttf功能自动朗读（挑战）
   - [ ]  发掘或制作简单易用的ttf音色训练方案
   - [ ]  用户自练音色实装
- [x]  优化OCR可使用cpu模式，让硬件条件不好的玩家也可以露出笑容
- [ ]  新增其他厂商的API接口
- [ ]  对网络错误、API配额耗尽等异常情况做容错处理
- [ ]  尝试实现常驻系统托盘，按快捷键唤起（可以先实现鼠标操作的快捷启动）
- [ ]  尝试双屏方案
- [ ]  优化运行环境自定义选项，玩家可以更方便选择torch版本