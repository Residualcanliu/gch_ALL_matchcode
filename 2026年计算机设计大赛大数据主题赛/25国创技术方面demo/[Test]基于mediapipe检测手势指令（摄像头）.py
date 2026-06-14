import cv2
import mediapipe as mp
import numpy as np
import time

# ---------------------- 配置参数 ----------------------
camera_index = 0  # 摄像头索引（笔记本内置=0，外接=1）
window_name = "Electric Vehicle OK Gesture Detection(made by gch)"
ok_print_cooldown = 1.0  # OK手势防抖（1秒内只打印一次）
last_ok_time = 0.0       # 上次打印"接单"的时间

# MediaPipe Hands配置
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
# 手部检测参数（调优后更适配实时检测）
hands = mp_hands.Hands(
    static_image_mode=False,    # 视频流模式（非静态图片）
    max_num_hands=1,            # 只检测1只手（优先右手）
    model_complexity=1,         # 模型复杂度（1=平衡速度/精度）
    min_detection_confidence=0.7,  # 检测置信度阈值
    min_tracking_confidence=0.7    # 跟踪置信度阈值
)
# ------------------------------------------------------

def classify_ok_gesture(hand_landmarks, frame_shape):
    """
    精准判断OK手势（基于MediaPipe 21个手部关键点）
    关键点索引：4=拇指尖，8=食指尖，12=中指尖，16=无名指尖，20=小指尖
    """
    h, w, _ = frame_shape
    # 1. 获取拇指尖和食指尖的像素坐标
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_xy = (int(thumb_tip.x * w), int(thumb_tip.y * h))
    index_xy = (int(index_tip.x * w), int(index_tip.y * h))
    
    # 2. 计算拇指-食指距离（OK手势核心：指尖靠近）
    distance = np.linalg.norm(np.array(thumb_xy) - np.array(index_xy))
    if distance > 40:  # 阈值可根据摄像头距离调整（30-50）
        return False
    
    # 3. 验证其他手指伸直（OK手势要求中指/无名指/小指伸直）
    mid_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    mid_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]  # 中指掌指关节
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]    # 无名指掌指关节
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]        # 小指掌指关节
    
    # 伸直判断：指尖y坐标 < 掌指关节y坐标（越往上越伸直）
    is_mid_straight = mid_tip.y < mid_mcp.y
    is_ring_straight = ring_tip.y < ring_mcp.y
    is_pinky_straight = pinky_tip.y < pinky_mcp.y
    
    return all([is_mid_straight, is_ring_straight, is_pinky_straight])

# 打开摄像头并优化参数
cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # 分辨率
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)             # 帧率

if not cap.isOpened():
    print(f"❌ 无法打开摄像头（索引：{camera_index}）")
    exit()

print("✅ MediaPipe手部检测已启动")
print(f"✅ 摄像头参数：1280×720 | 30FPS")
print("✅ 右手比OK手势 → 打印「接单」| 按 'q' 退出")

# 主循环
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ 无法获取摄像头画面，退出...")
        break
    
    # 1. 预处理：镜像翻转（适配第一视角）+ 转换为RGB（MediaPipe要求）
    frame = cv2.flip(frame, 1)  # 水平镜像，第一视角更自然
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_copy = frame.copy()
    
    # 2. MediaPipe手部检测
    results = hands.process(frame_rgb)
    is_ok_gesture = False
    
    if results.multi_hand_landmarks:
        # 遍历检测到的手（只取第一只，优先右手）
        for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            # 判断是否为右手
            hand_type = hand_info.classification[0].label
            if hand_type != "Right":
                continue  # 只检测右手
            
            # 绘制手部关键点和连线（可视化）
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                # 关键点样式：绿色
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                # 连线样式：蓝色
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )
            
            # 3. 判断OK手势
            if classify_ok_gesture(hand_landmarks, frame.shape):
                is_ok_gesture = True
                
                # 4. 防抖打印「接单」
                current_time = time.time()
                if current_time - last_ok_time > ok_print_cooldown:
                    print("📢 接单")
                    last_ok_time = current_time
    
    # 5. 绘制结果提示
    if is_ok_gesture:
        # OK手势：绿色提示
        cv2.putText(
            frame,
            "Gesturing 'OK' -> jiedan",
            (50, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),  # 绿色
            4
        )
    else:
        # 未检测到OK手势：红色提示
        cv2.putText(
            frame,
            "waiting ok...",
            (50, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255),  # 红色
            3
        )
    
    # 6. 显示画面
    cv2.imshow(window_name, frame)
    
    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🔚 退出程序...")
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
hands.close()  # 关闭MediaPipe检测器