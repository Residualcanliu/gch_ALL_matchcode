from DrissionPage import ChromiumPage
import csv
import pandas as pd
import jieba
import wordcloud
import os

# 创建文件
folder_path = r'D:\PythonObjectAll\26正大杯\vr校园视频评论\douyin'
file_path = os.path.join(folder_path, f'抖音vr评论数据1.csv')
f = open(file_path, mode='w', encoding='utf-8-sig', newline='')
# 字典写入方法
csv_writer = csv.DictWriter(f, fieldnames=['标题','昵称', '地区', '评论内容'])
# 写入表头
csv_writer.writeheader()

web='https://www.douyin.com/video/6799182542256868615'
# 打开浏览器
dp = ChromiumPage()
# 监听视频标题
dp.listen.start('aweme/detail/')
# 访问视频网站
dp.get(web)
# 等待监听加载
resp_detail = dp.listen.wait()
# 获取响应数据
json_data_detail = resp_detail.response.body
"""解析数据"""
# 键值对取值，提取视频详情信息
json_detail = json_data_detail['aweme_detail']
# 提取视频标题
video_title = json_detail['desc']
# 关闭浏览器
dp.quit()


# 打开浏览器
dp = ChromiumPage()

# 监听评论列表
dp.listen.start('comment/list/')
# 访问视频网站
dp.get(web)


# 构建循环翻页
for page in range(1,100):
    print(f'正在采集第{page}页的内容')
    # 等待监听加载
    resp = dp.listen.wait()
    # 获取响应数据
    json_data = resp.response.body
    """解析数据"""
    # 键值对取值，提取评论信息所在列表
    comments = json_data['comments']
    # 提取评论内容
    for index in comments:
        """提取具体信息"""
        try:
            ip_label = index['ip_label']
        except:
            ip_label = '未知'

        dit = {
            '标题':video_title,
            '昵称':index['user']['nickname'],
            '地区':ip_label,
            '评论内容':index['text']
        }
        #写入csv文件
        csv_writer.writerow(dit)
    # 定位底部元素
    next_page = dp.ele('css:.Rcc71LyU')
    #下滑操作
    dp.scroll.to_see(next_page)
dp.quit()
#
# """下面是可视化"""
# file_paths = [
#     r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐视频信息1.csv',
#     r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐视频信息2.csv',
#     r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐视频信息3.csv',
#     r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐视频信息4.csv',
#     r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐视频信息5.csv',
# ]
# all_comments = ''
# # jieba词典
# # 定义需要添加的词汇列表
# custom_words = [
#     ('非遗', 10000, 'n'),
#     ('传统技艺', 10000, 'n'),
#     ('民俗文化', 10000, 'n'),
#     ('#百young非遗计划', 10000, 'n'),
#     ('#非遗舞蹈', 10000, 'n'),
#     ('#非遗贺新春', 10000, 'n'),
#     ('#各地民俗舞起来', 10000, 'n'),
#     ('#抖音非遗计划', 10000, 'n'),
#     ('#千年非遗一拍入戏', 10000, 'n'),
#     ('#非遗守护人 ', 10000, 'n'),
#     ('#vivoX200系列舞台神器', 10000, 'n'),
#     ('木榨油', 10000, 'n'),
#     ('@抖音小助手', 10000, 'n'),
#
# ]
# for word, freq, tag in custom_words:
#     jieba.add_word(word, freq=freq, tag=tag)
# # 循环读取每个文件
# for file_path in file_paths:
#     try:
#         # 读取 CSV 文件
#         df = pd.read_csv(file_path)
#         # 提取评论内容列，并将其转换为字符串，去除换行符，然后添加到 all_comments 中
#         comments = ''.join([str(i).replace('\n', '') for i in df['地区']])
#         all_comments += comments
#     except FileNotFoundError:
#         print(f"文件 {file_path} 未找到，请检查文件路径。")
#     except KeyError:
#         print(f"文件 {file_path} 中未找到 '评论内容' 列，请检查列名。")
# # 结巴分词处理
# string = ' '.join(jieba.lcut(all_comments))
# # 词云图配置
# wc =wordcloud.WordCloud(
#     font_path='C:/Windows/Fonts/msyh.ttc',
#     width=1000,
#     height=760,
#     background_color='white',
#     stopwords={'让','来','《','里','已有','看','为','只','人','一个','中','着','在','与','。','大','老','我','啦','你','都','就','是','她','的','了','什么','和','吧','吗','还','我们','也','有','在‘,’都','这个','这'}
# )
# # 导入词汇
# wc.generate(string)
# # 导出词云图
# wc.to_file(r'C:\Users\gch\Desktop\正大杯\内容\抖音爬取内容\3.非遗音乐\非遗音乐评论ip词云图.png')
# print(string)
