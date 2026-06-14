from ultralytics import YOLO
import cv2
import os

# ---------------------- 核心配置 ----------------------
model_path = "yolov8m.pt"  # 模型路径
image_path = r"D:\PythonObjectAll\25国创技术方面\开车视角\开车第一视角2.png"  # 待检测的图片路径（替换成你的图片）
save_result = True  # 是否保存检测结果图片
save_dir = r"D:\PythonObjectAll\25国创技术方面\检测后视角"  # 结果保存目录

# 0=人，1=自行车，2=车，3=摩托车，5=公交车，7=卡车，9=红绿灯，
# 10=消防栓，11=路障（barrier），13=停止标志，67=围栏（fence）
target_classes = [0,1,2,3,5,7,9,10,11,13,67]

conf_threshold = 0.1
imgsz = 800  # 增大输入尺寸，提升小目标检测能力
window_name = "检测结果"
# ---------------------------------------------------------------------

model = YOLO(model_path)
print(f"检测目标：{[model.names[cls] for cls in target_classes]}")

# 检查图片
if not os.path.exists(image_path):
    print(f"图片不存在：{image_path}")
    exit()
frame = cv2.imread(image_path)
if frame is None:
    print(f"无法读取图片：{image_path}")
    exit()

# 优化检测参数：增大尺寸+低置信度+小目标增强
results = model(
    frame,
    classes=target_classes,
    conf=conf_threshold,
    imgsz=imgsz,
    augment=True,  # 开启数据增强（模拟不同光线/角度，提升低光场景检测）
    retina_masks=True  # 提升小目标的框精度
)

# 绘制结果
for result in results:
    frame_with_detections = result.plot(line_width=3, font_size=1.2)

# 打印结果
boxes = results[0].boxes
print(f"\n检测到的目标数：{len(boxes)}")
if len(boxes) > 0:
    for i, box in enumerate(boxes):
        print(f"目标 {i+1}：{model.names[int(box.cls)]}（置信度：{float(box.conf):.2f}）")

# 保存+显示
if save_result:
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"optimized_{os.path.basename(image_path)}")
    cv2.imwrite(save_path, frame_with_detections)
    print(f"结果保存至：{save_path}")

cv2.imshow(window_name, frame_with_detections)
cv2.waitKey(0)
cv2.destroyAllWindows()