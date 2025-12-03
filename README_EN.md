<div align="center">

# 实时屏幕AI翻译工具 | Real-time Screen AI Translator Tool
[中文](README.md) | English

</div>

## Introduction
This is a Python application for real-time translation of screen content into other languages. It uses local OCR (Optical Character Recognition) to extract text from selected screen areas, then translates it into Chinese using online AI.

## Features
- **Real-time Screenshot**: Capture the screen and generate screenshots.
- **OCR Recognition**: Extract text from screenshots.
- **AI Translation**: Translate extracted text using AI services.
- **Real-time Display**: Show translation results in real-time.

## Quick Start
1. Install uv to manage Python virtual environment. [Download uv](https://github.com/astral-sh/uv)
2. Clone this repository locally and enter the project directory:
```bash
git clone https://github.com/shaymin5/real-time_screen_AI_translator.git
cd real-time_screen_AI_translator
```
3. Create a `.env` file in the directory and add your Deepseek API key
```text
DEEPSEEK_API_KEY=your_api_key
```
4. Install dependencies with `uv`
```bash
uv sync
```
When installing torch, download speed may be slow due to overseas servers. Using a proxy can speed up the process. Currently, this operation defaults to downloading the cu128 (GPU) version of torch. If you don't have an NVIDIA graphics card, please download the CPU version. To download the CPU version, replace `https://download.pytorch.org/whl/cu128` in `pyproject.toml` with `https://download.pytorch.org/whl/cpu` or `https://pypi.tuna.tsinghua.edu.cn/simple` (the latter has faster download speeds in mainland China). If your device has specific torch version requirements, please modify `https://download.pytorch.org/whl/cu128` to the appropriate address.

5. Start running
```bash
uv run main.py
```
## Tips
- Current version recommends only selecting the translation area; avoid changing other settings.
- Currently only supports Deepseek API (cost-effective option). Planning to integrate faster AI translation services in the future.
- Currently only supports English to Chinese translation; planning to add more language options.
- CPU version of torch hasn't been tested yet. Interested users can help test performance differences. On RTX5060 8GB GPU, typical image OCR recognition speed is around 0.1 seconds.