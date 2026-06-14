from ultralytics import YOLO
import cv2

# ---------------------- 核心配置 ----------------------
model_path = "yolov8m.pt"  # 中大型模型
camera_index = 0  # 摄像头索引
# 需检测的目标类别（COCO数据集ID对应表，只保留核心目标）
# 类别ID对应：0=人，1=自行车，2=车，3=摩托车，5=公交车，7=卡车，9=红绿灯，13=_stop标志
target_classes = [0, 1, 2, 3, 5, 7, 9]
conf_threshold = 0.5
window_name = "外卖员视角道路检测"
# ---------------------------------------------------------------------

model = YOLO(model_path)
print(f"模型加载成功：{model_path}")
print(f"检测目标类别：{[model.names[cls] for cls in target_classes]}")

# 打开摄像头
cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    print(f"无法打开摄像头（索引：{camera_index}），请检查设备！")
    exit()

print(f"摄像头已开启，按 'q' 键退出...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法获取图像帧，退出...")
        break

    # 实时检测：只检测指定类别，过滤低置信度结果
    results = model(
        frame,
        stream=True,
        classes=target_classes,  # 只检测指定目标
        conf=conf_threshold,     # 置信度阈值（调高则更严格）
        imgsz=640                # 输入尺寸（640平衡速度和精度）
    )

    # 绘制检测结果（只显示指定目标）
    for result in results:
        # 自定义绘制样式（加粗边框、显示类别名称+置信度）
        frame_with_detections = result.plot(
            line_width=2,  # 边框粗细
            font_size=1.0  # 字体大小
        )

    # 显示结果
    cv2.imshow(window_name, frame_with_detections)

    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("退出程序...")
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()