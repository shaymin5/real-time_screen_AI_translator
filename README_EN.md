<div align="center">

# Real-time Screen AI Translator Tool
[中文](README.md) | English

</div>

## Introduction
This is a Python application for translating screen content into other languages in real time. It uses local OCR (Optical Character Recognition) to extract text from a selected screen area and then translates it into Chinese using an online AI service.

## Features
- **Real-time Screenshot**: Capture the screen and generate screenshots.
- **OCR Recognition**: Extract text from screenshots.
- **Online Translation**: Perform translation using the DeepSeek API.
- **Automatic Game UI Masking**: Automatically identify and mask game interface elements.

## Quick Start
1. Install `uv` to manage the Python virtual environment. [Download uv](https://github.com/astral-sh/uv).
2. Clone this repository locally and navigate to the project directory, or download the repository directly.
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```
3. Create a `.env` file in the directory and add your DeepSeek API key.
```text
DEEPSEEK_API_KEY=your_api_key_here
```
4. Install dependencies using `uv`.
```bash
uv sync
```
When installing `torch`, downloads from international servers are slow by default. Using a proxy can speed this up. Currently, this operation defaults to downloading the cu128 (GPU) version of torch. If you do not have an NVIDIA graphics card, please download the CPU version. To download the CPU version, replace `https://download.pytorch.org/whl/cu128` in `pyproject.toml` with `https://download.pytorch.org/whl/cpu` or `https://pypi.tuna.tsinghua.edu.cn/simple`. The latter offers faster download speeds within mainland China. If your device has specific torch version requirements, please modify the URL `https://download.pytorch.org/whl/cu128` accordingly.

5. Start the application.
```bash
uv run main.py
```

## Tips
- The first time you select a source language, you need to wait for the OCR model to download. Subsequent uses do not require downloading, and the speed will be much faster.
- Currently only supports the DeepSeek API, which is a cost-effective choice. Future updates may integrate faster AI translation services.
- Currently only supports translation from English to Chinese. Support for more languages is planned for future updates.
- Performance differences in OCR recognition speed: RTX 5060 8G takes about 0.1 seconds, causing a delay of 0.2 seconds; Ryzen 9500f takes about 0.3 seconds, causing a delay of 0.6 seconds.

## Important Note
This project uses the `pickle` module to load `.pk` files. The project itself does not include these files; they are generated during runtime and are only used to save settings and the masked word database. Do not trust `.pk` files from untrusted sources, as malicious `.pk` files may pose a security threat to your computer.

## Future Plans
- [ ] Asynchronous translation to improve user experience.
- [x] Add support for new languages.
- [ ] Open API interface prompt modification function, allowing users to customize translation services.
- [ ] Add TTS functionality for automatic text-to-speech (Challenging).
   - [ ] Explore or develop a simple and easy-to-use TTS voice training solution.
   - [ ] Implement user-trained voice models.
- [x] Optimize OCR to support CPU mode, allowing players with lower-end hardware to enjoy the tool.
- [ ] Add support for other manufacturers' API interfaces.
- [ ] Implement error handling for network errors, API quota exhaustion, and other exceptional cases.
- [ ] Attempt to implement a system tray resident application with hotkey activation (quick launch via mouse operations can be implemented first).
- [ ] Attempt dual-screen support.
- [ ] Optimize custom runtime environment options, allowing users to more easily select torch versions.