# Analyze/dim_reduction.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.manifold import TSNE

try:
    import prince
    if not hasattr(prince, 'FAMD'):
        from prince.famd import FAMD
    else:
        FAMD = prince.FAMD
except ImportError:
    FAMD = None
    print("[Warning] 'prince' library not found. PCA/FAMD may fail.")

class DimensionAnalyzer:
    def __init__(self, data, target_col='stroke', save_dir=None, timestamp=None, task_name='dim_red'):
        self.data = data
        self.target = data[target_col]
        self.features = data.drop(columns=[target_col])
        
        # 保存配置
        self.save_dir = save_dir
        self.timestamp = timestamp
        self.task_name = task_name
        
        self.num_cols = ['age', 'avg_glucose_level', 'bmi']
        self.num_cols = [c for c in self.num_cols if c in self.features.columns]
        self.cat_cols = [c for c in self.features.columns if c not in self.num_cols]

    def _save_plot(self, plot_type):
        """内部辅助函数：生成文件名并保存"""
        if self.save_dir and self.timestamp:
            # 命名规则：Task_Type_Timestamp.png
            # 例如：pca_famd_scatter_20251203_1430.png
            filename = f"{self.task_name}_{plot_type}_{self.timestamp}.png"
            full_path = os.path.join(self.save_dir, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"[Info] Plot saved: {full_path}")

    def plot_embedding(self, X_embedded, title, plot_type_suffix="scatter"):
        """通用绘图函数"""
        plt.figure(figsize=(10, 8))
        unique_targets = sorted(self.target.unique())
        if set(unique_targets).issubset({0, 1}):
            labels = self.target.map({0: 'No Stroke', 1: 'Stroke'})
        else:
            labels = self.target.astype(str)

        sns.scatterplot(
            x=X_embedded[:, 0], 
            y=X_embedded[:, 1], 
            hue=labels,
            palette={'No Stroke': 'skyblue', 'Stroke': 'red'} if 'No Stroke' in labels.values else None,
            alpha=0.7,
            s=60
        )
        plt.title(title, fontsize=15)
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')
        plt.legend(title='Condition')
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # 自动保存
        self._save_plot(plot_type_suffix)
        plt.show()

    def perform_pca_famd(self):
        """执行 FAMD 并保存结果"""
        if FAMD is None: return

        print("[Analysis] Performing FAMD...")
        try:
            famd = FAMD(n_components=2, n_iter=200, copy=True, check_input=True, engine='sklearn', random_state=42)
            X_famd = famd.fit_transform(self.features)
            
            # 1. 保存散点图
            self.plot_embedding(X_famd.values if hasattr(X_famd, 'values') else X_famd, 
                                "FAMD Visualization (Sample Distribution)",
                                plot_type_suffix="famd_scatter")
            
            # 2. 保存载荷图 (Loadings)
            print("[Analysis] Generating FAMD Loadings Plot...")
            if hasattr(famd, 'column_coordinates_'):
                coords = famd.column_coordinates_
            elif hasattr(famd, 'column_correlations'):
                coords = famd.column_correlations(self.features)
            else:
                return

            comp0_loadings = coords.iloc[:, 0].sort_values(ascending=False)
            
            plt.figure(figsize=(12, 6))
            sns.barplot(x=comp0_loadings.values, y=comp0_loadings.index, palette="viridis")
            plt.title("FAMD Loadings (Component 0) - Variable Contributions", fontsize=14)
            plt.xlabel("Correlation with Component 0", fontsize=12)
            plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
            plt.tight_layout()
            
            # 保存载荷图
            self._save_plot("famd_loadings")
            plt.show()

        except Exception as e:
            print(f"[Error] FAMD analysis failed: {e}")

    def perform_tsne(self):
        """执行 t-SNE 并保存结果"""
        print("[Analysis] Performing t-SNE...")
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.num_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), self.cat_cols)
            ])
        X_processed = preprocessor.fit_transform(self.features)
        
        try:
            tsne = TSNE(n_components=2, perplexity=40, max_iter=1000, random_state=42, n_jobs=-1)
        except TypeError:
            tsne = TSNE(n_components=2, perplexity=40, n_iter=1000, random_state=42, n_jobs=-1)

        X_tsne = tsne.fit_transform(X_processed)
        # 保存 t-SNE 散点图
        self.plot_embedding(X_tsne, "t-SNE Visualization", plot_type_suffix="tsne_scatter")
        print("[Analysis] t-SNE completed.")