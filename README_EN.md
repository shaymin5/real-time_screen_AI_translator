<div align="center">

# Real-time Screen AI Translator Tool | Real-time Screen AI Translator Tool
[中文](README.md) | English

</div>

## Introduction
This is a Python application for translating screen content into other languages in real-time. It uses local OCR (Optical Character Recognition) to extract text from a selected screen area, then translates it into Chinese using an online AI service.

## Features
- **Real-time Screenshot Capture**: Captures the screen and generates screenshots.
- **OCR Recognition**: Extracts text from screenshots.

## Quick Start
1. Install **uv** to manage the Python virtual environment. [Download uv](https://github.com/astral-sh/uv).
2. Clone this repository locally and navigate into the project directory, or download the repository directly.
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```
3. Create a `.env` file in the directory and add your Deepseek API key.
```text
DEEPSEEK_API_KEY=your_api_key_here
```
4. Install dependencies using `uv`.
```bash
uv sync
```
Downloading torch from overseas servers may be slow; using a proxy can speed it up. Currently, the default operation downloads the cu128 (GPU) version of torch. If you do not have an NVIDIA GPU, please download the CPU version. To download the CPU version, replace `https://download.pytorch.org/whl/cu128` in `pyproject.toml` with `https://download.pytorch.org/whl/cpu` or `https://pypi.tuna.tsinghua.edu.cn/simple`. The latter offers faster download speeds in mainland China.
If your device has specific torch version requirements, please modify `https://download.pytorch.org/whl/cu128` to the appropriate URL yourself.

5. Start the application.
```bash
uv run main.py
```

## Notes
- The first time you select a source language, you need to wait for the OCR model to download. Subsequent uses will not require downloading and will be much faster.
- Currently, only the Deepseek API is supported, which is a cost-effective choice. Faster AI translation options are being considered for future integration.
- Currently, only English-to-Chinese translation is supported. Support for additional languages is planned for the future.
- OCR recognition speed varies by hardware: An RTX 5060 8G takes about 0.1 seconds, causing a 0.2-second delay; a Ryzen 9500F takes about 0.3 seconds, causing a 0.6-second delay.

## Next Steps
- [ ] Implement asynchronous translation to improve user experience
- [x] Add support for new languages
- [ ] Enable API prompt modification, allowing users to customize translation services
- [ ] Implement TTS functionality for automatic reading (Challenging)
   - [ ] Explore or develop a simple and easy-to-use TTS voice training solution
   - [ ] Implement user-trained voice models
- [x] Optimize OCR to support CPU mode, allowing users with lower-end hardware to enjoy the tool
- [ ] Add API interfaces from other providers
- [ ] Implement error handling for network errors, exhausted API quotas, and other exceptions
- [ ] Attempt to implement a system tray resident mode with hotkey activation (mouse-operated quick start can be implemented first)
- [ ] Experiment with a dual-screen solution
- [ ] Optimize customizable runtime environment options, allowing users to more easily select torch versions