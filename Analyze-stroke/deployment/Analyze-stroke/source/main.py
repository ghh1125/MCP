# Analyze/main.py
import argparse
import os
import sys
import datetime
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from data_loader import DataLoader
from dim_reduction import DimensionAnalyzer
from models import ModelManager
from causal_module import CausalAnalyzer
from feature_selection import FeatureSelectionAnalyzer

class DualLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a", encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

def main():
    parser = argparse.ArgumentParser(description="Stroke Analysis Toolkit")
    
    parser.add_argument('--task', type=str, required=True, choices=['pca', 'tsne', 'prediction', 'causal', 'feature_selection'])
    parser.add_argument('--model', type=str, default='xgboost', choices=['nb', 'lr', 'svm', 'knn', 'dt', 'rf', 'xgboost', 'dnn'])
    parser.add_argument('--method', type=str, default='kbest', choices=['kbest', 'rfecv', 'chi2'])
    parser.add_argument('--treatment', type=str, default='gender')
    parser.add_argument('--file', type=str, default=r'D:\workspace\stroke\data\healthcare-dataset-stroke-data.csv')
    parser.add_argument('--session_id', type=str, default=None)

    args = parser.parse_args()

    LOG_ROOT = r"D:\workspace\stroke\Analyze\logs"
    if args.session_id:
        session_dir_name = args.session_id
    else:
        session_dir_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    CURRENT_LOG_DIR = os.path.join(LOG_ROOT, session_dir_name)
    os.makedirs(CURRENT_LOG_DIR, exist_ok=True)
    timestamp_file = datetime.datetime.now().strftime("%H%M%S_%f")
    log_filename = f"{args.task}_{args.model}_{args.method}_{args.treatment}_{timestamp_file}.log"
    log_path = os.path.join(CURRENT_LOG_DIR, log_filename)

    sys.stdout = DualLogger(log_path)

    print(f"========================================================")
    print(f"[Log] Session Folder: {session_dir_name}")
    print(f"[Log] Output saved to: {log_path}")
    print(f"========================================================\n")

    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found!")
        return

    VIS_DIR = r"D:\workspace\stroke\Analyze\visualization"
    os.makedirs(VIS_DIR, exist_ok=True)
    
    loader = DataLoader(args.file)
    df = loader.load_and_clean()

    if args.task in ['pca', 'tsne']:
        analyzer = DimensionAnalyzer(df, save_dir=VIS_DIR, timestamp=session_dir_name, task_name=args.task)
        if args.task == 'pca': analyzer.perform_pca_famd()
        elif args.task == 'tsne': analyzer.perform_tsne()

    elif args.task == 'prediction':
        X_train, X_test, y_train, y_test = loader.get_split_data()
        manager = ModelManager(X_train, y_train, X_test, y_test, save_dir=VIS_DIR, timestamp=session_dir_name)
        if args.model == 'dnn': manager.run_dnn()
        else: manager.run_sklearn_model(args.model)

    elif args.task == 'causal':
        # === 优化：智能领域编码 (Smart Domain Encoding) ===
        print("[Info] Pre-processing data for Causal Inference (Applying Domain Knowledge)...")
        
        # 1. 性别: Male=1, Female=0
        if 'gender' in df.columns:
            df['gender'] = df['gender'].map({'Male': 1, 'Female': 0, 'Other': 0}).fillna(0)
            print("  - Encoded 'gender': Male=1, Female/Other=0")

        # 2. 结婚: Yes=1, No=0
        if 'ever_married' in df.columns:
            df['ever_married'] = df['ever_married'].map({'Yes': 1, 'No': 0}).fillna(0)
            print("  - Encoded 'ever_married': Yes=1, No=0")

        # 3. 居住: Urban=1, Rural=0
        if 'Residence_type' in df.columns:
            df['Residence_type'] = df['Residence_type'].map({'Urban': 1, 'Rural': 0}).fillna(0)
            print("  - Encoded 'Residence_type': Urban=1, Rural=0")

        # 4. 吸烟: 按风险等级编码 (Ordinal)
        # 修正之前的字母顺序错误。假设：smokes > formerly > never/unknown
        if 'smoking_status' in df.columns:
            # 策略：将 'smokes' 和 'formerly' 视为有风险(1)，其他(0)
            # 或者使用 0, 1, 2 阶梯。这里为了 ATE 线性回归更准，建议二值化：是否吸烟
            # 但为了保留细节，我们使用风险阶梯：
            smoke_map = {'unknown': 0, 'Unknown': 0, 'never smoked': 0, 'formerly smoked': 1, 'smokes': 2}
            df['smoking_status'] = df['smoking_status'].map(smoke_map).fillna(0)
            print("  - Encoded 'smoking_status' (Ordinal): Never/Unknown=0, Formerly=1, Smokes=2")

        # 5. 工作类型: 标称变量无法直接线性回归
        # 策略：关注"高压力/私人部门" vs "其他"。
        if 'work_type' in df.columns:
            # 将 Private 和 Self-employed 设为 1，其他设为 0
            work_map = {
                'Private': 1, 'Self-employed': 1, 
                'Govt_job': 0, 'children': 0, 'Never_worked': 0
            }
            df['work_type'] = df['work_type'].map(work_map).fillna(0)
            print("  - Encoded 'work_type' (Binary): Private/Self-employed=1, Others=0")

        analyzer = CausalAnalyzer(df)
        analyzer.run_analysis(treatment_col=args.treatment)

    elif args.task == 'feature_selection':
        analyzer = FeatureSelectionAnalyzer(df, save_dir=VIS_DIR, timestamp=session_dir_name)
        if args.method == 'kbest': analyzer.run_select_kbest()
        elif args.method == 'rfecv': analyzer.run_rfecv()
        elif args.method == 'chi2': analyzer.run_chi2()

if __name__ == "__main__":
    main()