import pandas as pd
from snownlp import SnowNLP
import os  # 新增导入os模块，用于处理路径


def get_sentiment_score(text):
    try:
        s = SnowNLP(text)
        return round(s.sentiments, 2)
    except:
        return None


# -------------------------- 全局配置区（只需要改这里的路径和参数） --------------------------
PATH1 = r"D:\PythonObjectAll\26正大杯\vr校园视频评论"

# 你的VR评论文件路径列表
COMMENT_FILE_PATHS = [
    f"{PATH1}\\Bilibili\\B站vr课堂评论数据1.csv",
    f"{PATH1}\\douyin\\抖音vr评论数据1.csv"
]

# 合并后的输出文件名
OUTPUT_MERGED_PATH = "VR设备视频评论_合并情感分析.csv"
# --------------------------------------------------------------------------------------------------

all_data = []

# 遍历处理所有文件
for idx, file_path in enumerate(COMMENT_FILE_PATHS, 1):
    try:
        # 提前提取文件名，避开f-string里的反斜杠
        file_name = os.path.basename(file_path)

        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 检查是否存在"评论内容"列
        if "评论内容" not in df.columns:
            print(f"跳过文件 {idx} ({file_name})：未找到'评论内容'列")
            continue

        # 计算情感得分
        df['情感得分'] = df['评论内容'].apply(get_sentiment_score)

        # 添加来源文件列，方便后续区分
        df['来源文件'] = file_name

        all_data.append(df)
        print(f'文件 {idx} 处理完成：{file_name}')

    except Exception as e:
        print(f'处理文件 {idx} 时出错：{str(e)}')

# 合并所有文件的数据
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_df.to_csv(OUTPUT_MERGED_PATH, index=False, encoding='utf-8-sig')
    print(f'\n所有文件合并完成！共 {len(merged_df)} 条评论')
    print(f'已保存至：{OUTPUT_MERGED_PATH}')
else:
    print('未处理到任何有效数据，无法生成合并文件')