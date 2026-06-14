import pandas as pd
from snownlp import SnowNLP

def get_sentiment_score(text):
    try:
        s = SnowNLP(text)
        return round(s.sentiments, 2)
    except:
        return None

all_data = []

for i in range(1, 6):
    try:
        input_path = f'AI眼镜视频评论/weibo/微博ai眼镜评论数据{i}.csv'
        df = pd.read_csv(input_path)
        df['情感得分'] = df['评论内容'].apply(get_sentiment_score)

        all_data.append(df)

        print(f'第{i}个文件处理完成')
    except Exception as e:
        print(f'处理第{i}个文件时出错：{str(e)}')

# 合并所有文件的数据
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_path = '微博ai眼镜评论数据_合并情感分析.csv'
    merged_df.to_csv(merged_path, index=False)  # 不保存行索引
    print(f'所有文件合并完成！已保存至：{merged_path}')
else:
    print('未处理到任何有效数据，无法生成合并文件')