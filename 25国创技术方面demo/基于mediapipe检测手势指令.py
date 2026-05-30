import cv2
import mediapipe as mp
import os
import numpy as np

# ---------------------- 配置参数 ----------------------
input_image_path = r"D:\PythonObjectAll\25国创技术方面\开车视角\手势检测用图片.png"  
output_dir = r"D:\PythonObjectAll\25国创技术方面\检测后视角"
GESTURE_COMMANDS = {
    "ok": "确认命令",
    "fist": "停止/刹车",
    "open_hand": "前进/继续"
}
# ------------------------------------------------------

# 初始化MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

# 兼容中文路径的图片读取
def cv2_imread_chinese(path):
    stream = open(path, 'rb')
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)

# 路径校验 + 读取图片
if not os.path.exists(input_image_path):
    print(f"错误：图片文件不存在！路径：\n{input_image_path}")
    exit()
image = cv2_imread_chinese(input_image_path)
if image is None:
    print(f"错误：无法读取图片！请检查图片格式（仅支持PNG/JPG）")
    exit()
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ---------------------- 修复核心：OK手势判断函数 ----------------------
def classify_ok_gesture(hand_landmarks, image_shape):
    """
    正确判断OK手势：
    1. 拇指尖(4)和食指尖(8)距离近（形成圈）
    2. 中指(12)、无名指(16)、小指(20)伸直（指尖在中间关节上方）
    """
    h, w, _ = image_shape
    # 1. 获取关键点坐标（转换为像素值）
    # 拇指尖、食指尖
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    thumb_xy = (int(thumb_tip.x * w), int(thumb_tip.y * h))
    index_xy = (int(index_tip.x * w), int(index_tip.y * h))
    
    # 2. 计算拇指-食指距离（OK手势核心：指尖靠近）
    distance = np.linalg.norm(np.array(thumb_xy) - np.array(index_xy))
    
    # 3. 判断其他手指是否伸直（中/无名/小指：指尖y坐标 < 中间关节y坐标）
    # 关键点索引：10=中指中间关节，12=中指尖；14=无名指中间关节，16=无名指尖；18=小指中间关节，20=小指尖
    mid_joint_indices = [10, 14, 18]  # 中间关节
    tip_indices = [12, 16, 20]         # 指尖
    other_straight = True
    for mid_idx, tip_idx in zip(mid_joint_indices, tip_indices):
        mid_joint_y = hand_landmarks.landmark[mid_idx].y
        tip_y = hand_landmarks.landmark[tip_idx].y
        if tip_y >= mid_joint_y:  # 指尖在关节下方=手指弯曲
            other_straight = False
            break
    
    # 距离阈值（可根据图片分辨率调整，30-50都可以）
    return distance < 40 and other_straight

# ---------------------- 检测逻辑 ----------------------
results = hands.process(image_rgb)
output_image = image.copy()

if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
        # 绘制手部关键点
        mp_drawing.draw_landmarks(
            output_image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )

        # 调用修复后的手势判断函数
        if classify_ok_gesture(hand_landmarks, image.shape):
            gesture = "ok"
            command = GESTURE_COMMANDS[gesture]
            cv2.putText(
                output_image,
                f"hand: {gesture} → do: {command}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
        else:
            cv2.putText(
                output_image,
                "OK -> yes",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                5.0,
                (255, 255, 0),
                2
            )
else:
    cv2.putText(
        output_image,
        "未检测到手部",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 255),
        2
    )

# 保存结果（兼容中文路径）
os.makedirs(output_dir, exist_ok=True)
input_filename = os.path.basename(input_image_path)
output_path = os.path.join(output_dir, f"hand_gesture_{input_filename}")
cv2.imencode(os.path.splitext(output_path)[1], output_image)[1].tofile(output_path)
print(f"结果已保存至：{output_path}")

# 显示图片
cv2.imshow("第一视角手势检测结果", output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()