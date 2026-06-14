import time
import csv
import os
from DrissionPage import ChromiumPage

# 创建文件
folder_path = r'AI眼镜视频评论/weibo'
os.makedirs(folder_path, exist_ok=True)  # 确保文件夹存在
file_path = os.path.join(folder_path, f'微博ai眼镜评论数据5.csv')
f = open(file_path, mode='w', encoding='utf-8-sig', newline='')
csv_writer = csv.DictWriter(f, fieldnames=['标题', '昵称', '地区', '评论内容'])
csv_writer.writeheader()

web = 'https://weibo.com/5821048344/QazwbjDfl'
dp = ChromiumPage()
dp.listen.start('ajax/statuses/')  # 监听评论接口
dp.get(web)
time.sleep(5)

for page in range(1, 52):
    print(f'正在采集第{page}页的内容')
    dp.scroll.to_bottom()
    resp = dp.listen.wait()
    json_data = resp.response.body  # 获取接口返回的JSON数据

    # 关键：打印数据结构，确认实际格式（首次运行时打开）
    # print(f"第{page}页原始数据：", json_data)

    try:
        # 1. 先确认评论列表的正确路径（根据实际打印结果调整）
        # 可能的正确路径：json_data['data']['comments'] 或 json_data['comments'] 等
        comments = json_data.get('data', [])  # 先用get避免KeyError

        # 2. 确保comments是列表
        if not isinstance(comments, list):
            print(f"第{page}页评论格式错误，不是列表：{type(comments)}")
            continue

        # 3. 遍历评论，增加类型判断
        for index in comments:
            # 跳过非字典类型的元素
            if not isinstance(index, dict):
                print(f"第{page}页发现非字典元素：{index}")
                continue

            # 提取信息（带异常处理）
            try:
                user = index.get('user', {})  # 先获取user，默认空字典
                screen_name = user.get('screen_name', '未知昵称')
                ip_label = user.get('location', '未知地区')
                text_raw = index.get('text_raw', '无内容')

                dit = {
                    '标题': "#95后小伙手搓AI眼镜体验失明的一天#当世界陷入黑暗，科技能否成为照亮前路的光？上海95后AI开发者帆哥用半年时间给出了答案，他带领团队手搓的AI眼...",  # 你的标题
                    '昵称': screen_name,
                    '地区': ip_label,
                    '评论内容': text_raw
                }
                csv_writer.writerow(dit)
            except Exception as e:
                print(f"解析评论出错：{e}，评论数据：{index}")

    except Exception as e:
        print(f"第{page}页数据处理出错：{e}")

f.close()
dp.quit()