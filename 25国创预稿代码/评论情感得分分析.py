import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 全局配置：解决中文显示、设置高清分辨率、统一字号基准
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
plt.rcParams['axes.unicode_minus'] = False  # 负号显示
plt.rcParams['figure.dpi'] = 300  # 高清分辨率
plt.rcParams['font.size'] = 12  # 基础字号


# 定义函数：计算单个平台的情感得分统计指标和占比
def calculate_emotion_metrics(df, platform_name):
    """
    计算情感得分均值、中位数，及积极/中性/消极占比
    :param df: 平台评论数据DataFrame
    :param platform_name: 平台名称（用于打印标识）
    :return: positive_pct, neutral_pct, negative_pct（占比）
    """
    # 核心统计指标
    mean_score = df['情感得分'].mean()
    median_score = df['情感得分'].median()
    # 计算各情感极性占比
    positive_pct = (df['情感得分'] >= 0.6).mean() * 100
    neutral_pct = ((df['情感得分'] > 0.4) & (df['情感得分'] < 0.6)).mean() * 100
    negative_pct = (df['情感得分'] <= 0.4).mean() * 100

    # 打印该平台统计结果
    print(f"\n===== {platform_name} 情感分析结果 =====")
    print(f"情感得分均值：{mean_score:.2f}")
    print(f"情感得分中位数：{median_score:.2f}")
    print(f"积极评论占比：{positive_pct:.2f}%")
    print(f"中性评论占比：{neutral_pct:.2f}%")
    print(f"消极评论占比：{negative_pct:.2f}%")

    return positive_pct, neutral_pct, negative_pct


# ---------------------- 1. 读取三个平台的数据 ----------------------
# 请根据实际文件路径/名称修改！
file_paths = {
    'B站': '情感分析数据/B站ai眼镜评论数据_合并情感分析.csv',
    '抖音': '情感分析数据/抖音ai眼镜评论数据_合并情感分析.csv',
    '微博': '情感分析数据/微博ai眼镜评论数据_合并情感分析.csv'
}

# 存储各平台的占比结果
platform_metrics = {}
for platform, path in file_paths.items():
    df = pd.read_csv(path)
    platform_metrics[platform] = calculate_emotion_metrics(df, platform)

# ---------------------- 2. 绘制多平台分组柱状图 ----------------------
# 数据准备
categories = ['积极评论', '中性评论', '消极评论']  # 横轴：情感类型
platforms = ['B站', '抖音', '微博']  # 对比平台
bar_width = 0.2  # 柱子宽度
x = np.arange(len(categories))  # 横轴基准位置

# 创建画布（调整尺寸适配多平台对比）
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制每个平台的柱子（不同颜色区分）
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # B站(蓝)、抖音(橙)、微博(绿)
for i, platform in enumerate(platforms):
    # 每个平台的柱子偏移：B站左移、抖音居中、微博右移
    ax.bar(x + i * bar_width - bar_width, platform_metrics[platform],
           width=bar_width, label=platform, color=colors[i], alpha=0.8)

# 图表美化（解决字号偏小问题）
ax.set_title('B站/抖音/微博 情感极性占比对比', fontsize=16, pad=20)  # 标题字号放大
ax.set_xlabel('情感类型', fontsize=14, labelpad=10)  # 横轴标签
ax.set_ylabel('占比 (%)', fontsize=14, labelpad=10)  # 纵轴标签
ax.set_xticks(x)  # 调整横轴刻度位置
ax.set_xticklabels(categories, fontsize=12)  # 横轴刻度字号
ax.tick_params(axis='y', labelsize=12)  # 纵轴刻度字号
ax.legend(title='平台', fontsize=12, title_fontsize=12)  # 图例字号
ax.grid(axis='y', linestyle='--', alpha=0.3)  # 增加纵轴网格线，提升可读性

# 调整布局，避免标签重叠
plt.tight_layout()
# 显示图表
plt.savefig('单平台情感分析图.png', bbox_inches='tight', dpi=300)
plt.show()
