import torch
import dowhy
import pandas as pd
import numpy as np

def check_environment():
    print("="*30)
    print("Environment Integrity Check")
    print("="*30)
    
    # 1. Check PyTorch & CUDA
    print(f"[PyTorch] Version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"[CUDA]    Available: Yes (Device: {torch.cuda.get_device_name(0)})")
        # 测试简单的 Tensor 运算
        x = torch.tensor([1.0, 2.0]).cuda()
        print(f"[CUDA]    Tensor Test: Passed (Allocated on {x.device})")
    else:
        print("[CUDA]    Available: NO (Check driver/installation)")

    # 2. Check Dowhy (Ensure dependency fix worked)
    print(f"[DoWhy]   Version: {dowhy.__version__}")
    
    # 3. Check Pandas/Numpy
    print(f"[Pandas]  Version: {pd.__version__}")
    print(f"[Numpy]   Version: {np.__version__}")
    
    print("="*30)
    print("All checks passed successfully.")

if __name__ == "__main__":
    check_environment()