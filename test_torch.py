import torch
import subprocess
import sys

def diagnose_cuda_issue():
    """诊断 CUDA 不可用的原因"""
    print("=== CUDA 诊断报告 ===")
    
    # 1. 检查 PyTorch 版本和构建配置
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"PyTorch 构建配置: {torch.__config__.show()}")
    
    # 2. 检查 CUDA 可用性
    print(f"CUDA 可用: {torch.cuda.is_available()}")
    
    # 3. 检查是否有 NVIDIA 显卡
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 检测到 NVIDIA 显卡")
            print("nvidia-smi 输出:")
            print(result.stdout[:500])  # 只显示前500字符
        else:
            print("✗ 未检测到 NVIDIA 显卡或驱动未安装")
    except FileNotFoundError:
        print("✗ nvidia-smi 命令不存在，可能没有安装 NVIDIA 驱动")
    
    # 4. 检查 CUDA 工具包
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 检测到 CUDA 工具包")
            print(result.stdout)
        else:
            print("✗ 未检测到 CUDA 工具包")
    except FileNotFoundError:
        print("✗ nvcc 命令不存在，可能没有安装 CUDA 工具包")
    
    
    # 6. 检查 Python 环境
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件: {sys.executable}")

diagnose_cuda_issue()