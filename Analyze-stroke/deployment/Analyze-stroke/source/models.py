# Analyze/models.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline 

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class ModelManager:
    def __init__(self, X_train, y_train, X_test, y_test, save_dir=None, timestamp=None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        
        # 保存配置
        self.save_dir = save_dir
        self.timestamp = timestamp
        
        self.num_cols = ['age', 'avg_glucose_level', 'bmi']
        self.cat_cols = [c for c in X_train.columns if c not in self.num_cols]

    def _save_plot(self, model_name, content_type):
        """内部辅助函数：保存预测相关图片"""
        if self.save_dir and self.timestamp:
            # 命名规则：prediction_{Model}_{ContentType}_{Timestamp}.png
            # 例如：prediction_xgboost_feature_importance_20251203_1430.png
            filename = f"prediction_{model_name}_{content_type}_{self.timestamp}.png"
            full_path = os.path.join(self.save_dir, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"[Info] Plot saved: {full_path}")

    def _get_pipeline(self, classifier):
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.num_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.cat_cols)
            ],
            verbose_feature_names_out=False
        )
        pipeline = ImbPipeline(steps=[
            ('preprocessor', preprocessor),
            ('smote', SMOTE(random_state=42)), 
            ('classifier', classifier)
        ])
        return pipeline

    def evaluate(self, y_true, y_pred, y_prob=None, model_name="Model"):
        # ... (保持原有的 evaluate 逻辑不变)
        acc = accuracy_score(y_true, y_pred)
        sens = recall_score(y_true, y_pred)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1 = f1_score(y_true, y_pred)
        auc = roc_auc_score(y_true, y_prob) if y_prob is not None else "N/A"
        
        print(f"\n--- Results for {model_name} ---")
        print(f"Accuracy:    {acc:.4f}")
        print(f"Sensitivity: {sens:.4f}")
        print(f"Specificity: {spec:.4f}")
        print(f"F1 Score:    {f1:.4f}")
        print(f"ROC-AUC:     {auc}")
        return {'acc': acc, 'sens': sens, 'spec': spec, 'f1': f1, 'auc': auc}

    def run_sklearn_model(self, model_type):
        models_map = {
            'nb': GaussianNB(),
            'lr': LogisticRegression(max_iter=2000, class_weight='balanced'),
            'svm': SVC(probability=True, class_weight='balanced'),
            'knn': KNeighborsClassifier(),
            'dt': DecisionTreeClassifier(class_weight='balanced'),
            'rf': RandomForestClassifier(class_weight='balanced', random_state=42),
            'xgboost': XGBClassifier(scale_pos_weight=19, eval_metric='logloss', random_state=42)
        }
        
        if model_type not in models_map:
            raise ValueError(f"Unknown model type: {model_type}")
            
        print(f"[Training] Running {model_type}...")
        clf = models_map[model_type]
        pipeline = self._get_pipeline(clf)
        pipeline.fit(self.X_train, self.y_train)
        
        # === 1. 逻辑回归系数可视化 ===
        if model_type == 'lr':
            print("\n[Analysis] Extracting Logistic Regression Coefficients...")
            try:
                model = pipeline.named_steps['classifier']
                feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
                coefs = model.coef_[0]
                coef_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coefs})
                coef_df['Abs_Coef'] = coef_df['Coefficient'].abs()
                coef_df = coef_df.sort_values(by='Abs_Coef', ascending=False).head(15)
                
                plt.figure(figsize=(10, 8))
                colors = ['red' if x > 0 else 'skyblue' for x in coef_df['Coefficient']]
                sns.barplot(x='Coefficient', y='Feature', data=coef_df, palette=colors)
                plt.title('Top 15 Factors (LR Coefficients)')
                plt.xlabel('Coefficient Value')
                plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
                plt.tight_layout()
                
                # 保存
                self._save_plot(model_type, "coefficients")
                plt.show()
            except Exception as e: print(e)

        # === 2. 特征重要性 (XGBoost/RF/DT) ===
        elif model_type in ['xgboost', 'rf', 'dt']:
            try:
                print(f"\n[Analysis] Extracting Feature Importance for {model_type}...")
                model = pipeline.named_steps['classifier']
                feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
                importances = model.feature_importances_
                
                feat_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
                feat_imp = feat_imp.sort_values(by='Importance', ascending=False).head(10)
                
                plt.figure(figsize=(10, 6))
                sns.barplot(x='Importance', y='Feature', data=feat_imp, palette='viridis')
                plt.title(f'Top 10 Features - {model_type}')
                plt.tight_layout()
                
                # 保存
                self._save_plot(model_type, "feature_importance")
                plt.show()
            except Exception as e: print(e)
        
        # 预测与评估
        y_pred = pipeline.predict(self.X_test)
        y_prob = None
        if hasattr(pipeline, "predict_proba"):
            y_prob = pipeline.predict_proba(self.X_test)[:, 1]
        self.evaluate(self.y_test, y_pred, y_prob, model_name=model_type)

    def run_dnn(self):
        # 这里的 DNN 代码与之前保持一致，你可以选择性添加 loss curve 的绘图与保存
        # 为了简洁，这里仅保留核心结构
        print("[Training] Running DNN with Entity Embeddings...")
        # ... (PyTorch 数据处理与模型定义代码与之前一致) ...
        # 如果你需要在 DNN 中绘图，也可以调用 self._save_plot("dnn", "loss_curve")
        pass