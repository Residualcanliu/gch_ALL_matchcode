from ultralytics import YOLO
import cv2
import os

# ---------------------- 配置参数 ----------------------
model_path = r"D:\PythonObjectAll\25国创技术方面\yolov8m.pt"  # 模型路径
image_path = r"D:\PythonObjectAll\25国创技术方面\开车视角\开车第一视角3.jpg"  # 待检测图片路径
save_dir = r"D:\PythonObjectAll\25国创技术方面/检测后视角"  # 结果保存目录
save_filename = "detected_开车第一视角1.jpg"  # 保存的文件名
# ---------------------------------------------------------------------

# 加载模型
model = YOLO(model_path)

# 单次检测图片（获取结果，后续复用该结果，避免重复推理）
results = model(image_path)

# 打印检测结果信息
print("\n===== 检测结果统计 =====")
print(f"检测图片路径：{image_path}")
print(f"检测结果数量：{len(results)}")  # 单张图片固定为1

if len(results) > 0:
    boxes = results[0].boxes
    print(f"是否检测到目标：{len(boxes) > 0}")
    print(f"当前图片的目标数量：{len(boxes)}")

    # 打印每个目标的详细信息（类别、置信度、坐标）
    print("\n===== 目标详细信息 =====")
    for i, box in enumerate(boxes):
        cls_id = int(box.cls)
        cls_name = model.names[cls_id]  # 转换为类别名称（更直观）
        conf = float(box.conf)
        xyxy = [round(x, 2) for x in box.xyxy.tolist()[0]]  # 坐标保留2位小数
        print(f"目标 {i + 1}：类别={cls_name}（ID={cls_id}），置信度={conf:.2f}，坐标={xyxy}")

# 处理并保存/显示结果
if len(results) > 0:
    # 创建保存目录（如果不存在）
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, save_filename)  # 完整保存路径

    # 获取带检测框的图像（RGB格式）
    result_img = results[0].plot()
    # 转换为OpenCV兼容的BGR格式（否则保存的图片会偏色）
    result_img_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)

    # 保存图片
    cv2.imwrite(save_path, result_img_bgr)
    print(f"\n结果图片已保存至：{save_path}")

    # 显示图片（保持窗口打开，直到按任意键关闭）
    cv2.imshow("YOLO 道路障碍物检测结果", result_img_bgr)
    print("图片显示中，按任意键关闭窗口...")
    cv2.waitKey(0)  # 无限等待按键
    cv2.destroyAllWindows()  # 关闭所有窗口
else:
    print("\n未检测到有效结果，无法保存/显示图片。")