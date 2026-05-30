import time

from DrissionPage import ChromiumPage
import csv
import pandas as pd
import jieba
import wordcloud
import os

# 创建文件
folder_path = r'vr校园视频评论/Bilibili'
file_path = os.path.join(folder_path, f'B站vr课堂评论数据2.csv')
f = open(file_path, mode='w', encoding='utf-8-sig', newline='')
# 字典写入方法
csv_writer = csv.DictWriter(f, fieldnames=['标题','昵称', '地区', '评论内容'])
# 写入表头
csv_writer.writeheader()

web='https://www.bilibili.com/video/BV1gi9CY2EpR/'

# # 打开浏览器
# dp = ChromiumPage()
# # 监听视频标题
# dp.listen.start('view/')
# # 访问视频网站
# dp.get(web)
# # 等待监听加载
# resp_detail = dp.listen.wait()
# # 获取响应数据
# json_data_detail = resp_detail.response.body
# """解析数据"""
# # 键值对取值，提取视频详情信息
# json_detail = json_data_detail['data']
# # 提取视频标题
# video_title = json_detail['View']['title']
# dp.quit()

# 打开浏览器
dp = ChromiumPage()

# 监听评论列表
dp.listen.start('reply/wbi/')
# 访问视频网站
dp.get(web)


# 构建循环翻页
for page in range(1,52):
    print(f'正在采集第{page}页的内容')
    # 划到底部
    dp.scroll.to_bottom()
    # 等待监听加载
    resp = dp.listen.wait()
    # 获取响应数据
    json_data = resp.response.body
    """解析数据"""
    # 键值对取值，提取评论信息所在列表
    comments = json_data['data']['replies']
    # 提取评论内容
    for index in comments:
        """提取具体信息"""
        try:
            ip_label = index['ip_label']
        except:
            ip_label = '未知'

        dit = {
            '标题':"当物理老师在课上突然掏出VisionPro",
            '昵称':index['member']['uname'],
            '地区':ip_label,
            '评论内容':index['content']['message']
        }
        #写入csv文件
        csv_writer.writerow(dit)
