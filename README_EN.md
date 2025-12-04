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

## Tips
- For the current version, it is recommended to only select the translation area and not modify other settings.
- Currently only supports the Deepseek API, which is a cost-effective choice. Plans are in place to integrate faster AI translation services in the future.
- Currently only supports translation from English to Chinese. Support for additional languages is planned for the future.
- The CPU version of torch has not been tested. If anyone is interested, please feel free to help test the performance difference. On an RTX5060 8GB GPU, typical OCR recognition speed for images is around 0.1 seconds.

## Next Steps
0. Establish a testing framework to facilitate testing new features.
1. Add support for new languages.
2. Open up API prompt customization functionality, allowing users to customize translation services.
3. Add TTS (Text-to-Speech) functionality for automatic reading (challenging).
   1. Explore or create a simple and easy-to-use TTS voice training solution.
   2. Implement user-trained voices.
4. Optimize and add support for new OCR engines, enabling users with less powerful hardware to enjoy the tool.
5. Add API interfaces from other providers.
6. Implement error handling for exceptions such as network errors and exhausted API quotas.
7. Attempt to create a system tray resident application that can be summoned via hotkeys (a quick-launch via mouse operation can be implemented first).
8. Experiment with a dual-screen solution.
9. Optimize and expand runtime environment customization options, allowing users to more easily select torch versions.