# Analyze/run_all_causal.py
import os
import time
import datetime
import subprocess
import re
import pandas as pd
import numpy as np
# 引入刚才写的绘图模块
from plot_utils import plot_from_excel

# === 配置区域 ===
FACTORS = [
    'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
    'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'
]

def parse_log_output(output_text):
    """从日志文本中提取指标"""
    metrics = {'ATE': np.nan, 'New Effect': np.nan, 'P-Value': np.nan}
    
    # 正则提取浮点数 (支持负数和多位小数)
    ate_match = re.search(r"\[Result\] Causal Estimate \(ATE\): (-?\d+\.\d+)", output_text)
    if ate_match: metrics['ATE'] = float(ate_match.group(1))

    ne_match = re.search(r"Refutation New Effect: (-?\d+\.\d+)", output_text)
    if ne_match: metrics['New Effect'] = float(ne_match.group(1))

    pv_match = re.search(r"Refutation p-value: (-?\d+\.\d+)", output_text)
    if pv_match: metrics['P-Value'] = float(pv_match.group(1))
        
    return metrics

def run_batch_analysis():
    # 1. 创建会话文件夹
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_BatchCausal_Summary")
    LOG_ROOT = r"D:\workspace\stroke\Analyze\logs"
    SESSION_DIR = os.path.join(LOG_ROOT, session_id)
    os.makedirs(SESSION_DIR, exist_ok=True)

    print(f"=== 开始批量因果分析 ===")
    print(f"=== 结果保存路径: {SESSION_DIR} ===")

    results_list = []

    # 2. 循环执行任务
    for i, factor in enumerate(FACTORS):
        print(f"\n>>> [{i+1}/{len(FACTORS)}] 分析因素: {factor} ...")
        
        # 调用 main.py 并传递 session_id
        cmd = ["python", "main.py", "--task", "causal", "--treatment", factor, "--session_id", session_id]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            metrics = parse_log_output(result.stdout)
            metrics['Factor'] = factor
            results_list.append(metrics)
            print(f"    -> [提取成功] ATE={metrics['ATE']}, P-Val={metrics['P-Value']}")

        except subprocess.CalledProcessError as e:
            print(f"    -> [执行错误] {e.stderr}")
        except Exception as e:
            print(f"    -> [未知错误] {e}")
        
        time.sleep(0.5)

    # 3. 保存 Excel (关键修改：保留4位小数)
    print("\n=== 正在生成 Excel 报告 ===")
    if results_list:
        results_df = pd.DataFrame(results_list)
        
        # 调整列顺序
        cols = ['Factor', 'ATE', 'New Effect', 'P-Value']
        results_df = results_df[cols]

        # === 核心修改：强制保留4位小数 ===
        # 注意：这里是将数据本身四舍五入，不仅仅是显示格式
        numeric_cols = ['ATE', 'New Effect', 'P-Value']
        results_df[numeric_cols] = results_df[numeric_cols].astype(float).round(4)
        
        excel_name = f"Causal_Summary_{session_id}.xlsx"
        excel_path = os.path.join(SESSION_DIR, excel_name)
        
        try:
            results_df.to_excel(excel_path, index=False)
            print(f"[Output] Excel 表格已保存 (4位小数): {excel_path}")
            
            # 4. 调用绘图模块 (模块化调用)
            print("=== 正在调用绘图模块 ===")
            plot_from_excel(excel_path)
            
        except Exception as e:
            print(f"[Error] 保存或绘图失败: {e}")
    else:
        print("[Warning] 结果列表为空，跳过保存。")

    print(f"\n=== 任务全部完成！目录: {SESSION_DIR} ===")

if __name__ == "__main__":
    run_batch_analysis()