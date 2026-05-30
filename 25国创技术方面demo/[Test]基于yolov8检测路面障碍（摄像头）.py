from ultralytics import YOLO
import cv2

# ---------------------- 配置参数 ----------------------
model_path = r"D:\PythonObjectAll\25国创技术方面\yolov8n.pt"
camera_index = 0  # 摄像头索引（0=默认摄像头，1=外接摄像头，依此类推）
window_name = "实时道路障碍物检测"
# ---------------------------------------------------------------------

# 加载YOLO模型
model = YOLO(model_path)
print(f"模型加载成功：{model_path}")

# 打开摄像头（0为默认摄像头，可根据实际设备修改）
cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    print(f"无法打开摄像头（索引：{camera_index}），请检查设备连接！")
    exit()

print(f"摄像头已开启，按 'q' 键退出...")

# 实时检测循环
while True:
    # 读取一帧图像
    ret, frame = cap.read()
    if not ret:
        print("无法获取图像帧，退出程序...")
        break

    # 对当前帧进行检测（stream=True 优化实时性能）
    results = model(frame, stream=True)

    # 处理检测结果并绘制到帧上
    for result in results:
        # 绘制检测框、类别名称和置信度（result.plot() 自动处理）
        frame_with_detections = result.plot()  # 直接在原图上绘制

    # 显示实时检测结果
    cv2.imshow(window_name, frame_with_detections)

    # 等待按键（1ms延迟，按 'q' 键退出）
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("用户按下 'q' 键，退出程序...")
        break

# 释放资源
cap.release()  # 关闭摄像头
cv2.destroyAllWindows()  # 关闭所有显示窗口
print("程序已退出，资源已释放。")