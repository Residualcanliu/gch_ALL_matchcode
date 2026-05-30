import mss
import numpy as np
import easyocr
import cv2
import os
import warnings

NAME = "千幻魔镜 XR"
x1 = 122
y1 = 515
x2 = 1286
y2 = 1268

# 屏蔽警告
warnings.filterwarnings("ignore")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 1. 初始化 EasyOCR 模型 (第一次运行会自动下载模型，需联网)
print("正在加载 OCR 模型")
# lang_list=['ch_sim', 'en'] 表示识别简体中文和英文
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)


def capture_and_ocr(region, output_file=f"{NAME}评论.txt"):
    with mss.mss() as sct:
        # 截取屏幕
        sct_img = sct.grab(region)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 调用 EasyOCR 识别
        # detail=0 表示只返回文字，不返回坐标
        result = reader.readtext(img, detail=1)

        extracted_text = []
        if result:
            for (bbox, text, confidence) in result:
                if confidence > 0.5:  # EasyOCR 的置信度阈值可以稍微调低一点
                    extracted_text.append(text)

        # 输出并保存
        if extracted_text:
            print("\n识别成功，内容如下：")
            print("-" * 50)
            with open(output_file, "a", encoding="utf-8") as f:
                for t in extracted_text:
                    print(t)
                    f.write(t + "\n")
            print("-" * 50)
            print(f"[已追加保存到 {output_file}]")
        else:
            print("未识别到有效文字（可能是该区域没有字，或者需要微调坐标）")


# ================= 修正后的屏幕区域配置 =================
monitor = {
    "top": y1,          # 起始 Y 坐标 (顶部)
    "left": x1,         # 起始 X 坐标 (左侧)
    "width": x2 - x1,   # 宽度 = 右x - 左x
    "height": y2 - y1   # 高度 = 下y - 上y
}

# ================= 主程序循环 =================
print(f"目标区域已设定: {monitor}")
print("准备就绪！请确保电商评论区在该区域内。")
print("按 Enter 键开始识别当前屏幕，按 Ctrl+C 退出程序...\n")

try:
    while True:
        input("按下 Enter 键截取并识别...")
        capture_and_ocr(monitor)
        print("\n---------------------------")
except KeyboardInterrupt:
    print("\n程序已结束。")