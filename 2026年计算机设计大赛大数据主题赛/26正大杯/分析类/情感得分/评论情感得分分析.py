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


# ---------------------- 1. 读取两个平台的数据（仅需修改这里的文件名） ----------------------
# 对应你截图里的两个CSV文件，和代码同目录直接写文件名即可
file_paths = {
    '视频平台': 'VR设备视频评论_合并情感分析.csv',
    '电商平台': 'VR设备电商评论_合并情感分析.csv'
}

# 存储各平台的占比结果
platform_metrics = {}
for platform, path in file_paths.items():
    df = pd.read_csv(path)
    platform_metrics[platform] = calculate_emotion_metrics(df, platform)

# ---------------------- 2. 绘制双平台分组柱状图 ----------------------
# 数据准备
categories = ['积极评论', '中性评论', '消极评论']  # 横轴：情感类型（和原代码保持不变）
platforms = ['视频平台', '电商平台']  # 对比平台（修改为你的两个维度）
bar_width = 0.35  # 双柱子适配的宽度
x = np.arange(len(categories))  # 横轴基准位置

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制每个平台的柱子（不同颜色区分）
colors = ['#1f77b4', '#ff7f0e']  # 视频平台(蓝)、电商平台(橙)
for i, platform in enumerate(platforms):
    # 双柱子居中偏移：左移半个宽度、右移半个宽度
    ax.bar(x + (i - 0.5) * bar_width, platform_metrics[platform],
           width=bar_width, label=platform, color=colors[i], alpha=0.8)

# 图表美化（横纵坐标完全和原代码保持不变）
ax.set_title('视频平台/电商平台 VR设备评论情感极性占比对比', fontsize=16, pad=20)
ax.set_xlabel('情感类型', fontsize=14, labelpad=10)  # 横轴不变
ax.set_ylabel('占比 (%)', fontsize=14, labelpad=10)  # 纵轴不变
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.legend(title='平台类型', fontsize=12, title_fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 调整布局，避免标签重叠
plt.tight_layout()
# 保存并显示图表
# plt.savefig('视频 and 电商平台情感对比图.png', bbox_inches='tight', dpi=300)
plt.show()