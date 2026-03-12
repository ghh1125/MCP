# Analyze/run_all_causal.py
import os
import time
import datetime

# 1. 生成本次批量任务的唯一会话ID (文件夹名)
session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_BatchCausal")

print(f"=== 开始批量因果分析 ===")
print(f"=== 所有日志将统一保存在: Analyze/logs/{session_id} ===")

factors = [
    'gender', 
    'age', 
    'hypertension', 
    'heart_disease', 
    'ever_married', 
    'work_type', 
    'Residence_type', 
    'avg_glucose_level', 
    'bmi', 
    'smoking_status'
]

for i, factor in enumerate(factors):
    print(f"\n>>> [{i+1}/{len(factors)}] 正在分析: {factor} ...")
    
    # 2. 调用 main.py 时传入 --session_id
    # 这样 main.py 就会把日志放进同一个文件夹，而不是新建文件夹
    cmd = f"python main.py --task causal --treatment {factor} --session_id {session_id}"
    
    os.system(cmd)
    
    # 稍微暂停，避免CPU过热或文件IO冲突
    time.sleep(1)

print(f"\n=== 批量分析完成！请查看文件夹: Analyze/logs/{session_id} ===")