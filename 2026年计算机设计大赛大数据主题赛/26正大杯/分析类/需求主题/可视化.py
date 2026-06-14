import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
plt.rcParams['axes.unicode_minus'] = False  # 负号显示

# ---------------------- 1. 定义所有数据 ----------------------
# 电商平台 - 需求数据
ecommerce_demand = {
    "themes": ["画质清晰", "佩戴轻便", "续航延长",
               "近视适配优化", "防眩晕效果提升"],
    "freq": [68, 52, 45, 38, 18],
    "sentiment": [0.82, 0.79, 0.81, 0.77, 0.75]
}

# 电商平台 - 痛点数据
ecommerce_pain = {
    "themes": ["佩戴压鼻梁", "近视适配差", "续航短",
               "眩晕", "教学资源少"],
    "freq": [19, 15, 12, 10, 9],
    "sentiment": [0.32, 0.28, 0.35, 0.25, 0.38]
}

# 视频平台 - 需求数据
video_demand = {
    "themes": ["教学场景适配", "防眩晕", "性价比高",
               "轻便佩戴", "多人同步课堂", "多学科覆盖"],
    "freq": [102, 85, 76, 68, 52, 51],
    "sentiment": [0.91, 0.88, 0.85, 0.83, 0.93, 0.87]
}

# 视频平台 - 痛点数据
video_pain = {
    "themes": ["担心眩晕", "价格高", "教学资源少",
               "操作复杂", "维护难"],
    "freq": [42, 35, 28, 15, 8],
    "sentiment": [0.21, 0.27, 0.33, 0.31, 0.36]
}


# ---------------------- 2. 通用绘图函数 ----------------------
def plot_priority_matrix(data, title, save_filename):
    themes = data["themes"]
    freq = data["freq"]
    sentiment = data["sentiment"]
    x = np.arange(len(themes))
    width = 0.6  # 柱子宽度

    # 创建画布和双轴（适度放大画布，适配更大字体）
    fig, ax1 = plt.subplots(figsize=(16, 8), dpi=120)
    ax2 = ax1.twinx()

    # 绘制提及频次（柱状图，蓝色斜纹）
    bars = ax1.bar(x, freq, width, color='#85a8d0', hatch='//', label='提及频次')

    # 计算并标注优先级（频次 × 情感得分）- 字体放大
    priorities = [f * s for f, s in zip(freq, sentiment)]
    for i, (bar, prio) in enumerate(zip(bars, priorities)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + max(freq) * 0.02,
                 f'优先级: {prio:.1f}',
                 ha='center', va='bottom', fontsize=22)  # 从12→14

    # 绘制平均情感得分（折线图+圆点，棕色）
    line = ax2.plot(x, sentiment, color='#a0522d', marker='o', markersize=12,  # 圆点从10→12
                    linewidth=4, label='平均情感得分')  # 线条从3→4

    # 图表样式设置 - 字体全面放大
    ax1.set_title(title, fontsize=30, pad=20)  # 标题从16→20
    ax1.set_xlabel('主题', fontsize=25, labelpad=12)  # 坐标轴标签从14→16
    ax1.set_ylabel('提及频次', fontsize=20, color='#4682b4')
    ax2.set_ylabel('平均情感得分', fontsize=20, color='#a0522d')

    # 设置x轴标签：水平显示，居中对齐 - 字体放大
    ax1.set_xticks(x)
    ax1.set_xticklabels(themes, rotation=0, ha='center', fontsize=24)

    # 新增：放大y轴刻度字体
    ax1.tick_params(axis='y', labelsize=20)  # 左y轴（提及频次）
    ax2.tick_params(axis='y', labelsize=20)  # 右y轴（平均情感得分）

    # 调整y轴范围
    ax1.set_ylim(0, max(freq) * 1.15)
    ax2.set_ylim(0, 1.05)

    # 合并图例 - 字体放大
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=18)  # 从12→14

    # 网格线
    ax1.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()

    # 保存图表（命名不变）
    fig.savefig(save_filename, dpi=150, bbox_inches='tight')
    plt.close(fig)  # 关闭画布释放内存
    return fig


# ---------------------- 3. 生成并保存所有图表 ----------------------
# 电商需求图（保存命名不变）
fig1 = plot_priority_matrix(
    ecommerce_demand,
    "电商平台-需求主题优先级矩阵（频次×情感得分）",
    "电商平台-需求主题优先级矩阵.png"
)

# 电商痛点图（保存命名不变）
fig2 = plot_priority_matrix(
    ecommerce_pain,
    "电商平台-痛点主题优先级矩阵（频次×情感得分）",
    "电商平台-痛点主题优先级矩阵.png"
)

# 视频平台需求图（保存命名不变）
fig3 = plot_priority_matrix(
    video_demand,
    "视频平台-需求主题优先级矩阵（频次×情感得分）",
    "视频平台-需求主题优先级矩阵.png"
)

# 视频平台痛点图（保存命名不变）
fig4 = plot_priority_matrix(
    video_pain,
    "视频平台-痛点主题优先级矩阵（频次×情感得分）",
    "视频平台-痛点主题优先级矩阵.png"
)

print("所有图表已保存完成！字体已整体放大，命名保持不变。")