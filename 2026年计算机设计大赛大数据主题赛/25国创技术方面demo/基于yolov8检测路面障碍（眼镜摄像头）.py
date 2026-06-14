# python版本：3.11及以下
# 使用指南：
# 一、本功能基于yolo开源库实现，启动前确保存在“yolov8n.pt”文件，否则会自动下载，如有疑问请咨询专业人士，请勿私自修改
# 二、文件中主要类和函数的功能说明：
# 1. Config类：检测系统配置参数类，包含模型路径、摄像头索引、镜像翻转开关、显示窗口名称、需要检测的目标类别等配置信息
# 2. RoadObstacleDetector类：路面障碍物检测核心类，负责模型加载、摄像头初始化、图像处理及检测等核心功能
#    - __init__：初始化检测器，接收配置参数，初始化模型、摄像头等属性，打印镜像配置状态
#    - load_model：加载YOLO模型，成功返回True，失败返回False并记录错误日志
#    - init_camera：初始化摄像头，打开指定索引的摄像头，成功返回True，失败返回False并记录错误日志
#    - _mirror_frame：私有方法，根据配置对图像帧进行镜像翻转处理（水平翻转）
#    - process_detection：处理单帧图像检测，先进行镜像处理，再执行YOLO检测，提取并返回含检测框的图像帧及检测到的目标列表
#    - run_detection：运行实时检测主循环，循环读取摄像头帧，处理检测，输出提示信息，显示图像，响应退出按键
#    - _print_warnings：私有方法，对检测到的目标输出提示信息（如“小心行人!”）
#    - release_resources：释放摄像头资源，关闭所有显示窗口，停止检测运行
# 3. main函数：程序主入口，初始化配置和检测器，加载模型、初始化摄像头后启动实时检测，程序结束时输出退出信息

from ultralytics import YOLO
import cv2
import logging
from typing import Tuple, Optional, List, Dict, Callable, ABC, abstractmethod

# ---------------------- 扩展接口定义 ----------------------
class ObstacleProcessor(ABC):
    """障碍物处理抽象基类，用于扩展检测后的处理逻辑"""
    @abstractmethod
    def process(self, frame: cv2.Mat, objects: List[str]) -> cv2.Mat:
        """处理检测结果的抽象方法"""
        pass

class WarningGenerator(ABC):
    """警告生成器抽象基类，用于扩展警告方式"""
    @abstractmethod
    def generate(self, objects: List[str], class_map: Dict[str, str]) -> None:
        """生成警告的抽象方法"""
        pass

# ---------------------- 配置参数 ----------------------
class Config:
    """检测系统配置参数类"""
    # 模型配置
    MODEL_PATH = r"D:\PythonObjectAll\25国创技术方面\yolov8n.pt"
    # 摄像头配置
    CAMERA_INDEX = 0
    ENABLE_MIRROR = True
    # 显示配置
    WINDOW_NAME = "实时道路障碍物检测"
    # 检测目标配置
    TARGET_CLASSES = {
        "person": "行人",
        "car": "车辆",
        "truck": "卡车",
        "bicycle": "自行车",
        "motorbike": "摩托车",
        "dog": "动物",
        "cat": "动物"
    }
    # 扩展配置
    EXTENSIONS = {
        "processor": None,  # 可配置自定义处理器
        "warning_generator": None  # 可配置自定义警告生成器
    }

# ---------------------- 核心功能模块 ----------------------
class RoadObstacleDetector:
    """路面障碍物检测核心类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.camera = None
        self.running = False
        self.processors: List[ObstacleProcessor] = []  # 处理器列表
        self.warning_generators: List[WarningGenerator] = []  # 警告生成器列表
        
        # 注册默认处理器和警告生成器
        self._register_default_extensions()
        
        # 外部回调函数（预留）
        self.on_detection: Optional[Callable[[cv2.Mat, List[str]], None]] = None

    def _register_default_extensions(self):
        """注册默认的扩展组件"""
        # 添加默认处理器
        class DefaultProcessor(ObstacleProcessor):
            def process(self, frame: cv2.Mat, objects: List[str]) -> cv2.Mat:
                return frame  # 默认不做额外处理
        
        # 添加默认警告生成器
        class DefaultWarningGenerator(WarningGenerator):
            def generate(self, objects: List[str], class_map: Dict[str, str]) -> None:
                if objects:
                    unique_objects = list(set(objects))
                    for obj in unique_objects:
                        logger.warning(f"小心{class_map[obj]}!")
        
        self.register_processor(DefaultProcessor())
        self.register_warning_generator(DefaultWarningGenerator())
        
        # 加载配置中的扩展
        if self.config.EXTENSIONS["processor"]:
            self.register_processor(self.config.EXTENSIONS["processor"])
        if self.config.EXTENSIONS["warning_generator"]:
            self.register_warning_generator(self.config.EXTENSIONS["warning_generator"])

    def register_processor(self, processor: ObstacleProcessor):
        """注册自定义处理器"""
        self.processors.append(processor)
        logger.info(f"已注册障碍物处理器: {processor.__class__.__name__}")

    def register_warning_generator(self, generator: WarningGenerator):
        """注册自定义警告生成器"""
        self.warning_generators.append(generator)
        logger.info(f"已注册警告生成器: {generator.__class__.__name__}")

    def load_model(self) -> bool:
        """加载YOLO模型"""
        try:
            self.model = YOLO(self.config.MODEL_PATH)
            logger.info(f"模型加载成功：{self.config.MODEL_PATH}")
            return True
        except Exception as e:
            logger.error(f"模型加载失败：{str(e)}")
            return False

    def init_camera(self) -> bool:
        """初始化摄像头"""
        try:
            self.camera = cv2.VideoCapture(self.config.CAMERA_INDEX)
            if not self.camera.isOpened():
                logger.error(f"无法打开摄像头（索引：{self.config.CAMERA_INDEX}）")
                return False
            
            logger.info(f"摄像头初始化成功（索引：{self.config.CAMERA_INDEX}）")
            return True
        except Exception as e:
            logger.error(f"摄像头初始化失败：{str(e)}")
            return False

    def _mirror_frame(self, frame) -> cv2.Mat:
        """镜像翻转处理"""
        if self.config.ENABLE_MIRROR:
            return cv2.flip(frame, 1)
        return frame

    def process_detection(self, frame) -> Tuple[Optional[cv2.Mat], list]:
        """处理单帧图像检测"""
        detected_objects = []
        
        try:
            frame = self._mirror_frame(frame)
            results = self.model(frame, stream=True)
            
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = self.model.names[class_id]
                    
                    if class_name in self.config.TARGET_CLASSES and confidence > 0.5:
                        detected_objects.append(class_name)
                
                frame_with_detections = result.plot()
                
                # 应用所有注册的处理器
                for processor in self.processors:
                    frame_with_detections = processor.process(frame_with_detections, detected_objects)
                
                # 触发外部回调
                if self.on_detection:
                    self.on_detection(frame_with_detections, detected_objects)
                    
                return frame_with_detections, detected_objects
            
            return frame, detected_objects
            
        except Exception as e:
            logger.error(f"检测处理失败：{str(e)}")
            return frame, detected_objects

    def run_detection(self):
        """运行实时检测主循环"""
        if not self.model or not self.camera:
            logger.error("模型或摄像头未初始化，请先完成初始化")
            return
        
        self.running = True
        logger.info("开始实时检测，按 'q' 键退出...")
        
        try:
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    logger.warning("无法获取图像帧，尝试重新获取...")
                    continue
                
                processed_frame, detected_objects = self.process_detection(frame)
                
                # 生成警告
                for generator in self.warning_generators:
                    generator.generate(detected_objects, self.config.TARGET_CLASSES)
                
                cv2.imshow(self.config.WINDOW_NAME, processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    logger.info("用户按下 'q' 键，准备退出...")
        
        except Exception as e:
            logger.error(f"检测过程发生错误：{str(e)}")
        finally:
            self.release_resources()

    def release_resources(self):
        """释放所有资源"""
        if self.camera:
            self.camera.release()
            logger.info("摄像头资源已释放")
        
        cv2.destroyAllWindows()
        logger.info("所有窗口已关闭")
        
        self.running = False

# ---------------------- 主程序入口 ----------------------
def main():
    """主函数：初始化并启动检测系统"""
    config = Config()
    detector = RoadObstacleDetector(config)
    
    # 添加自定义处理器（演示用）
    class CustomProcessor(ObstacleProcessor):
        def process(self, frame: cv2.Mat, objects: List[str]) -> cv2.Mat:
            if objects:
                cv2.putText(frame, f"检测到{len(objects)}个目标", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame
    
    detector.register_processor(CustomProcessor())
    
    if not detector.load_model():
        return
    if not detector.init_camera():
        return
    
    detector.run_detection()
    logger.info("程序已正常退出")

if __name__ == "__main__":
    # 日志配置
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    main()