# Analyze/plot_utils.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

# === 样式配置 ===
COLORS = {
    'ATE': "#0AB3F0",          # 亮蓝色 (文字)
    'ATE_Line': "#0AB3F0CA",   # 带透明度 (线和填充)
    'New Effect': "#F61467",   # 亮粉红 (文字)
    'New Effect_Line': "#F61467EE", # 带透明度 (线)
    'P-Value': '#2A9D8F',      # 青绿色
    'Threshold': '#F4A261',    # 橙色
    'ZeroLine': '#FF0000',     # 鲜红色
    'Grid': '#E0E0E0',         # 浅灰色 (内部网格)
    'Spine': '#555555'         # 深灰色 (最外圈边界)
}

def add_offset_labels(ax, angles, radii, labels, color, position='right'):
    """
    辅助函数：在数据点旁边添加数值标签，支持左右偏移
    """
    if position == 'left':
        xytext = (-8, 0) 
        ha = 'right'     
    else:
        xytext = (8, 0)  
        ha = 'left'      

    for angle, radius, label in zip(angles, radii, labels):
        ax.annotate(
            str(label), 
            xy=(angle, radius), 
            xytext=xytext,
            textcoords='offset points',
            color=color, 
            size=9, 
            weight='bold',
            ha=ha, 
            va='center',
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7)
        )

def draw_effect_chart(df, save_path):
    """
    绘制效应大小雷达图 (ATE & New Effect)
    """
    plot_df = df.copy()
    categories = plot_df['Factor'].tolist()
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))
    
    # === 0. 优化网格线 & 边界线 ===
    
    # A. 内部网格：保持浅灰色虚线
    ax.grid(True, color=COLORS['Grid'], linestyle='--', linewidth=1, alpha=0.8)
    
    # B. 最外圈边界 (Spine)：修改为深灰色实线
    ax.spines['polar'].set_visible(True)           # 确保显示
    ax.spines['polar'].set_color(COLORS['Spine'])  # 深灰色
    ax.spines['polar'].set_linestyle('solid')      # 实线
    ax.spines['polar'].set_linewidth(1.5)          # 稍微加粗
    
    # 1. 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='black', size=13, weight='heavy')
    
    # 2. 设置刻度
    ax.set_yticklabels([])
    ax.set_ylim(0, 1)
    
    # 3. 数据归一化
    max_ate = plot_df['ATE'].abs().max()
    max_ne = plot_df['New Effect'].abs().max()
    global_max = max(max_ate, max_ne)
    if global_max == 0: global_max = 1e-9
    
    r_ate = (0.5 + 0.5 * (plot_df['ATE'] / global_max)).tolist()
    r_ne = (0.5 + 0.5 * (plot_df['New Effect'] / global_max)).tolist()
    r_ate += r_ate[:1]
    r_ne += r_ne[:1]
    
    # 4. 绘图
    
    # 鲜红色的 Zero Effect 线 (虚线)
    circle_points = np.linspace(0, 2*np.pi, 100)
    ax.plot(circle_points, [0.5]*100, color=COLORS['ZeroLine'], linestyle='--', linewidth=2, label='Zero Effect (0)', zorder=2)
    
    # ATE
    ax.plot(angles, r_ate, linewidth=3, color=COLORS['ATE_Line'], label='ATE (Causal Estimate)')
    ax.fill(angles, r_ate, color=COLORS['ATE_Line'], alpha=0.1)
    ax.scatter(angles[:-1], r_ate[:-1], color=COLORS['ATE'], s=80, zorder=5)
    
    # New Effect
    ax.plot(angles, r_ne, linewidth=2, linestyle=':', color=COLORS['New Effect_Line'], label='Refutation')
    ax.scatter(angles[:-1], r_ne[:-1], facecolor='none', edgecolor=COLORS['New Effect'], s=80, marker='D', linewidth=2, zorder=6)
    
    # 5. 数值标注 (分离)
    labels_ate = plot_df['ATE'].round(4).tolist()
    labels_ne = plot_df['New Effect'].round(4).tolist()
    
    add_offset_labels(ax, angles[:-1], r_ate[:-1], labels_ate, color=COLORS['ATE'], position='left')
    add_offset_labels(ax, angles[:-1], r_ne[:-1], labels_ne, color=COLORS['New Effect'], position='right')
    
    # 6. 图饰
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title(f"Causal Effect Size (Split Labels)\nMax Scale = +/- {global_max:.4f}", size=16, weight='bold', y=1.1)
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"[PlotUtils] Effect Size chart saved to: {save_path}")
    plt.close()

def draw_pvalue_chart(df, save_path):
    """
    绘制显著性雷达图 (P-Value)
    """
    plot_df = df.copy()
    categories = plot_df['Factor'].tolist()
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))
    
    # === 优化网格线 & 边界线 ===
    ax.grid(True, color=COLORS['Grid'], linestyle='--', linewidth=1, alpha=0.8)
    
    ax.spines['polar'].set_visible(True)
    ax.spines['polar'].set_color(COLORS['Spine'])
    ax.spines['polar'].set_linestyle('solid')
    ax.spines['polar'].set_linewidth(1.5)
    
    # 1. 标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='black', size=13, weight='heavy')
    
    # 2. 刻度
    ax.set_rlabel_position(0)
    plt.yticks([0.05, 0.5, 1.0], ["P=0.05", "0.5", "1.0"], color="gray", size=10)
    ax.set_ylim(0, 1) 
    
    # 3. 数据
    r_pv = plot_df['P-Value'].tolist()
    r_pv += r_pv[:1]
    
    # 4. 绘图
    circle_points = np.linspace(0, 2*np.pi, 100)
    ax.plot(circle_points, [0.05]*100, color=COLORS['Threshold'], linestyle='-', linewidth=2, label='Threshold (P=0.05)')
    
    ax.plot(angles, r_pv, linewidth=2, color=COLORS['P-Value'], label='P-Value (Raw)')
    ax.fill(angles, r_pv, color=COLORS['P-Value'], alpha=0.1)
    
    # 标记显著点
    sig_indices = [i for i, p in enumerate(plot_df['P-Value']) if p <= 0.05]
    if sig_indices:
        sig_angles = [angles[i] for i in sig_indices]
        sig_radii = [r_pv[i] for i in sig_indices]
        ax.scatter(sig_angles, sig_radii, color='red', s=100, marker='*', zorder=10, label='Significant (P<=0.05)')
    
    # 5. 数值标注
    def add_simple_labels(ax, angles, radii, labels):
         for angle, radius, label in zip(angles, radii, labels):
            ax.text(angle, radius, str(label), color='#333333', size=9, weight='bold',
                    ha='center', va='center', bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))

    labels_pv = plot_df['P-Value'].round(4).tolist()
    add_simple_labels(ax, angles[:-1], r_pv[:-1], labels_pv)
    
    # 6. 图饰
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    title_text = "Statistical Significance (Raw P-Values)\n(Center = More Significant)"
    plt.title(title_text, size=16, weight='bold', y=1.1)
    
    note = "Note: Points inside the orange circle (P<0.05)\nare statistically significant."
    plt.text(1.3, 0, note, transform=ax.transAxes, fontsize=10, 
             bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"[PlotUtils] P-Value chart saved to: {save_path}")
    plt.close()

def plot_from_excel(excel_path, output_dir=None):
    if not os.path.exists(excel_path):
        print(f"[Error] 文件不存在: {excel_path}")
        return

    print(f"[PlotUtils] Reading data from: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
        
        if output_dir is None:
            output_dir = os.path.dirname(excel_path)
        
        base_name = os.path.splitext(os.path.basename(excel_path))[0]
        
        path_effect = os.path.join(output_dir, base_name + "_Effect_Labeled.png")
        draw_effect_chart(df, path_effect)
        
        path_pval = os.path.join(output_dir, base_name + "_PValue_Labeled.png")
        draw_pvalue_chart(df, path_pval)

    except Exception as e:
        print(f"[Error] 绘图失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, required=True, help="Path to excel file")
    args = parser.parse_args()
    plot_from_excel(args.file)