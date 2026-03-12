# Analyze/feature_selection.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 引入卡方检验和归一化
from sklearn.feature_selection import SelectKBest, mutual_info_classif, RFECV, chi2
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import StratifiedKFold

class FeatureSelectionAnalyzer:
    def __init__(self, data, target_col='stroke', save_dir=None, timestamp=None):
        self.data = data
        self.target = data[target_col]
        self.features = data.drop(columns=[target_col])
        
        self.save_dir = save_dir
        self.timestamp = timestamp
        
        self.num_cols = ['age', 'avg_glucose_level', 'bmi']
        self.num_cols = [c for c in self.num_cols if c in self.features.columns]
        self.cat_cols = [c for c in self.features.columns if c not in self.num_cols]
        
        # 通用预处理管道 (用于互信息和 RFECV)
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.num_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.cat_cols)
            ],
            verbose_feature_names_out=False
        )

    def _save_plot(self, method_name, plot_name):
        if self.save_dir and self.timestamp:
            filename = f"feature_selection_{method_name}_{plot_name}_{self.timestamp}.png"
            full_path = os.path.join(self.save_dir, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"[Info] Plot saved: {full_path}")

    def run_select_kbest(self):
        """策略 1: 互信息 (Mutual Information)"""
        print("[Analysis] Running SelectKBest (Mutual Information)...")
        X_processed = self.preprocessor.fit_transform(self.features)
        feature_names = self.preprocessor.get_feature_names_out()
        
        selector = SelectKBest(score_func=mutual_info_classif, k='all')
        selector.fit(X_processed, self.target)
        
        df_scores = pd.DataFrame({'Feature': feature_names, 'Score': selector.scores_})
        df_scores = df_scores.sort_values(by='Score', ascending=False)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Score', y='Feature', data=df_scores, palette='viridis')
        plt.title('Feature Importance via Mutual Information')
        plt.xlabel('Mutual Information Score')
        plt.tight_layout()
        self._save_plot("kbest_mutual_info", "scores")
        plt.show()

    def run_rfecv(self):
        """策略 2: 递归特征消除 (RFECV)"""
        print("[Analysis] Running RFECV...")
        X_processed = self.preprocessor.fit_transform(self.features)
        feature_names = self.preprocessor.get_feature_names_out()
        
        clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
        rfecv = RFECV(estimator=clf, step=1, cv=StratifiedKFold(5), scoring='f1')
        rfecv.fit(X_processed, self.target)
        
        print(f"[Result] Optimal features: {rfecv.n_features_}")
        
        n_features = range(1, len(rfecv.cv_results_['mean_test_score']) + 1)
        scores = rfecv.cv_results_['mean_test_score']
        
        plt.figure(figsize=(10, 6))
        plt.plot(n_features, scores, marker='o', color='b')
        plt.xlabel("Number of Features")
        plt.ylabel("CV F1 Score")
        plt.title(f"RFECV Performance (Optimal: {rfecv.n_features_})")
        plt.axvline(x=rfecv.n_features_, color='r', linestyle='--')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        self._save_plot("rfecv", "performance_curve")
        plt.show()

    def run_chi2(self):
        """
        策略 3: 卡方检验 (Chi-Square Test) - 新增
        注意：卡方检验要求输入非负，因此数值变量需使用 MinMaxScaler。
        """
        print("[Analysis] Running Chi-Square Test...")
        
        # 1. 定义卡方专用预处理器 (使用 MinMaxScaler 确保非负)
        chi2_preprocessor = ColumnTransformer(
            transformers=[
                ('num', MinMaxScaler(), self.num_cols), # 关键修改
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.cat_cols)
            ],
            verbose_feature_names_out=False
        )
        
        # 2. 转换数据
        X_processed = chi2_preprocessor.fit_transform(self.features)
        feature_names = chi2_preprocessor.get_feature_names_out()
        
        # 3. 计算卡方统计量和 P值
        # chi2 返回两个数组: (chi2_scores, p_values)
        chi2_scores, p_values = chi2(X_processed, self.target)
        
        # 4. 整理结果
        df_results = pd.DataFrame({
            'Feature': feature_names, 
            'Chi2_Score': chi2_scores,
            'P_Value': p_values
        })
        
        # 按分数排序 (分数越高，相关性越强)
        df_results = df_results.sort_values(by='Chi2_Score', ascending=False)
        
        # 打印前10个显著特征
        print("\n[Result] Top 10 Features by Chi-Square Score:")
        print(df_results[['Feature', 'Chi2_Score', 'P_Value']].head(10))
        
        # 5. 可视化 (Chi2 Score)
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Chi2_Score', y='Feature', data=df_results, palette='magma')
        plt.title('Feature Importance via Chi-Square Test')
        plt.xlabel('Chi-Square Statistics (Higher means more dependent)')
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        self._save_plot("chi2", "scores")
        plt.show()
        
        # 额外提示 P值
        print("\n[Note] P-Value < 0.05 通常表示统计学显著相关。")