import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# 全局配置（解决中文、负号显示问题）
mpl.rcParams.update(mpl.rcParamsDefault)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = True
plt.rcParams['mathtext.fontset'] = 'dejavusans'

# 核心数据
models = [
    'CVIT模型',
    'CVIT模型（不带VIT）',
    '传统CNN模型',
    'ViT-Base模型',
    '通用CNN+Transformer'
]
params = [2.1141, 2.1173, 2.4881, 85.2741, 90.3877]  # 参数量（M）
accuracy = [98.62, 97.75, 98.47, 97.06, 98.75]        # 测试集准确率（%）

# 定义样式
colors = ['#2E86AB', '#F18F01']  # 参数量-蓝色，准确率-橙色
width = 0.35  # 柱子宽度（并列布局需小于0.5）
x = np.arange(len(models))  # 模型的x轴位置

# 创建画布和双Y轴
fig, ax1 = plt.subplots(figsize=(12, 7))

# 绘制参数量柱子（左Y轴，对数刻度）
bars1 = ax1.bar(x - width/2, params, width, label='参数量（M）', color=colors[0], alpha=0.8)
ax1.set_xlabel('模型类型', fontsize=12)
ax1.set_ylabel('参数量（M）', fontsize=12, color=colors[0])
ax1.set_yscale('log')  # 对数刻度适配参数量的量级差异
ax1.tick_params(axis='y', labelcolor=colors[0])
ax1.grid(axis='y', alpha=0.3)

# 创建右Y轴，绘制准确率柱子
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width/2, accuracy, width, label='准确率（%）', color=colors[1], alpha=0.8)
ax2.set_ylabel('准确率（%）', fontsize=12, color=colors[1])
ax2.set_ylim(96, 99.5)  # 限定范围，突出准确率差异
ax2.tick_params(axis='y', labelcolor=colors[1])

# 添加数值标签（参数量）
for bar, val in zip(bars1, params):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
             f'{val:.2f}', ha='center', va='bottom', fontsize=9, color=colors[0])

# 添加数值标签（准确率）
for bar, val in zip(bars2, accuracy):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.08,
             f'{val:.2f}%', ha='center', va='bottom', fontsize=9, color=colors[1])

# 图表标题和样式优化（核心修复：移除pad参数，用y调整标题位置）
fig.suptitle('各模型参数量与准确率对比', fontsize=16, fontweight='bold', y=0.98)
ax1.set_xticks(x)
ax1.set_xticklabels(models, rotation=15)  # X轴标签旋转，避免重叠

# 合并图例（双Y轴的图例整合）
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

# 隐藏多余边框
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)

# 调整布局，避免标签重叠
plt.tight_layout(rect=[0, 0, 1, 0.95])

# 保存高清图片

plt.show()