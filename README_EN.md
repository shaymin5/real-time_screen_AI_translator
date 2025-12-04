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
- [ ] Asynchronous translation to enhance user experience  
- [ ] Add support for new languages  
- [ ] Enable API prompt customization, allowing users to configure translation services  
- [ ] Implement TTS (Text-to-Speech) auto-read feature (Challenge)  
   - [ ] Explore or create a simple and easy-to-use TTS voice training solution  
   - [ ] Implement user-trained voice models  
- [ ] Optimize and expand OCR engine support, ensuring smooth performance for users with lower-end hardware  
- [ ] Integrate API interfaces from other providers  
- [ ] Improve error handling for network issues, API quota exhaustion, and other exceptions  
- [ ] Implement a system tray resident feature with hotkey activation (starting with mouse-operated quick launch)  
- [ ] Explore dual-screen support solutions  
- [ ] Enhance customizable runtime environment options for easier Torch version selection