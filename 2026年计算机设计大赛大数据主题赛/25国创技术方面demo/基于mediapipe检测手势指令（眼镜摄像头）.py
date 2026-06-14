# python版本：3.11及以下
# 使用指南：
# 一、本功能基于mediapipe开源库实现，如有疑问请咨询专业人士，请勿私自修改
# 二、文件中主要函数的功能说明：
# 1. is_finger_straight：判断手指是否伸直，通过比较指尖与掌指关节的y坐标（指尖y < 掌指关节y则视为伸直）
# 2. is_finger_bent：判断手指是否弯曲，通过比较指尖与掌指关节的y坐标（指尖y > 掌指关节y则视为弯曲）
# 3. classify_ok_gesture：判断是否为OK手势，条件为拇指尖与食指尖距离近（归一化距离<0.05），且中指、无名指、小指伸直
# 4. classify_2_gesture：判断是否为2手势（食指、中指伸直，其他手指弯曲），检查对应手指的伸直/弯曲状态
# 5. classify_7_gesture：判断是否为7手势（拇指、食指伸直，其他手指弯曲），检查对应手指的伸直/弯曲状态
# 主程序逻辑：打开摄像头并配置参数，循环读取图像帧，根据配置进行镜像翻转，通过mediapipe处理手部关键点，
# 识别右手的OK、2、7手势（带防抖处理，避免频繁检测），在图像上绘制关键点和手势信息，响应退出按键并释放资源

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import List, Callable, Dict, Optional, Tuple, ABC, abstractmethod

# ---------------------- 扩展接口定义 ----------------------
class GestureClassifier(ABC):
    """手势分类器抽象基类，用于扩展新的手势识别"""
    @abstractmethod
    def classify(self, hand_landmarks) -> Optional[str]:
        """
        手势分类
        Returns: 手势名称或None
        """
        pass

class GestureAction(ABC):
    """手势动作抽象基类，用于扩展手势对应的动作"""
    @abstractmethod
    def execute(self, gesture: str) -> None:
        """执行手势对应的动作"""
        pass

# ---------------------- 配置参数类 ----------------------
class GestureConfig:
    """手势识别配置参数"""
    def __init__(self):
        self.camera_index = 0
        self.window_name = "Glasses Camera Gesture Detection"
        self.gesture_cooldown = 1.0
        self.mirror_flip = True
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 20
        self.max_hands = 1
        self.detection_confidence = 0.7
        self.tracking_confidence = 0.6

# ---------------------- 核心功能模块 ----------------------
class HandGestureDetector:
    """手势识别核心类"""
    
    def __init__(self, config: GestureConfig):
        self.config = config
        self.cap = None
        self.hands = None
        self.running = False
        self.last_detect_time = 0.0
        self.current_gesture = None
        
        # 注册系统
        self.classifiers: List[GestureClassifier] = []  # 分类器列表
        self.actions: Dict[str, List[GestureAction]] = {}  # 手势-动作映射
        self._register_default_components()
        
        # 外部回调（预留）
        self.on_gesture_detected: Optional[Callable[[str], None]] = None

    def _register_default_components(self):
        """注册默认的手势分类器"""
        # 默认手势分类器
        class DefaultGestureClassifier(GestureClassifier):
            def __init__(self, detector):
                self.detector = detector
                
            def is_finger_straight(self, tip_landmark, mcp_landmark):
                return tip_landmark.y < mcp_landmark.y
                
            def is_finger_bent(self, tip_landmark, mcp_landmark):
                return tip_landmark.y > mcp_landmark.y
                
            def classify_ok(self, hand_landmarks):
                thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                mid_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
                
                mid_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]
                ring_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]
                pinky_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
                
                distance = np.linalg.norm([
                    thumb_tip.x - index_tip.x,
                    thumb_tip.y - index_tip.y
                ])
                if distance > 0.05:
                    return False
                    
                return all([
                    self.is_finger_straight(mid_tip, mid_mcp),
                    self.is_finger_straight(ring_tip, ring_mcp),
                    self.is_finger_straight(pinky_tip, pinky_mcp)
                ])
                
            def classify_2(self, hand_landmarks):
                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                mid_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
                
                index_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
                mid_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]
                ring_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]
                pinky_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
                
                return all([
                    self.is_finger_straight(index_tip, index_mcp),
                    self.is_finger_straight(mid_tip, mid_mcp),
                    self.is_finger_bent(thumb_tip, index_mcp),
                    self.is_finger_bent(ring_tip, ring_mcp),
                    self.is_finger_bent(pinky_tip, pinky_mcp)
                ])
                
            def classify_7(self, hand_landmarks):
                thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                mid_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
                
                thumb_ip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP]
                index_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
                mid_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]
                ring_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]
                pinky_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
                
                return all([
                    self.is_finger_straight(thumb_tip, thumb_ip),
                    self.is_finger_straight(index_tip, index_mcp),
                    self.is_finger_bent(mid_tip, mid_mcp),
                    self.is_finger_bent(ring_tip, ring_mcp),
                    self.is_finger_bent(pinky_tip, pinky_mcp)
                ])
                
            def classify(self, hand_landmarks) -> Optional[str]:
                if self.classify_ok(hand_landmarks):
                    return "ok"
                elif self.classify_7(hand_landmarks):
                    return "7"
                elif self.classify_2(hand_landmarks):
                    return "2"
                return None
        
        self.register_classifier(DefaultGestureClassifier(self))

    def register_classifier(self, classifier: GestureClassifier):
        """注册自定义手势分类器"""
        self.classifiers.append(classifier)
        print(f"已注册手势分类器: {classifier.__class__.__name__}")

    def register_action(self, gesture: str, action: GestureAction):
        """为特定手势注册动作"""
        if gesture not in self.actions:
            self.actions[gesture] = []
        self.actions[gesture].append(action)
        print(f"为手势 '{gesture}' 注册动作: {action.__class__.__name__}")

    def init_mediapipe(self):
        """初始化MediaPipe配置"""
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.max_hands,
            model_complexity=0,
            min_detection_confidence=self.config.detection_confidence,
            min_tracking_confidence=self.config.tracking_confidence
        )

    def init_camera(self) -> bool:
        """初始化摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.config.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            if not self.cap.isOpened():
                print(f"❌ 无法打开摄像头（索引：{self.config.camera_index}）")
                return False
            
            print("✅ 摄像头初始化成功")
            return True
        except Exception as e:
            print(f"❌ 摄像头初始化失败：{str(e)}")
            return False

    def process_gestures(self, frame: cv2.Mat) -> Tuple[cv2.Mat, Optional[str]]:
        """处理手势识别"""
        if self.config.mirror_flip:
            frame = cv2.flip(frame, 1)
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        detected_gesture = None
        
        if results.multi_hand_landmarks and results.multi_handedness:
            hand_landmarks = results.multi_hand_landmarks[0]
            hand_type = results.multi_handedness[0].classification[0].label
            
            if hand_type == "Right":  # 仅处理右手
                # 绘制手部关键点
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # 调用所有分类器进行识别
                current_time = time.time()
                if current_time - self.last_detect_time > self.config.gesture_cooldown:
                    for classifier in self.classifiers:
                        gesture = classifier.classify(hand_landmarks)
                        if gesture:
                            detected_gesture = gesture
                            self.last_detect_time = current_time
                            break
        
        return frame, detected_gesture

    def run_detection(self):
        """运行手势检测主循环"""
        if not self.cap or not self.hands:
            print("❌ 摄像头或MediaPipe未初始化")
            return
            
        self.running = True
        print("✅ 手势检测启动成功")
        print(f"当前配置：镜像翻转={'开启' if self.config.mirror_flip else '关闭'}")
        print("支持手势：1（食指）、2（食指+中指）、7（拇指+食指）、OK")
        print("按 'q' 退出程序")
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ 无法获取摄像头画面，退出...")
                    break
                
                processed_frame, gesture = self.process_gestures(frame)
                self.current_gesture = gesture
                
                # 执行手势对应的动作
                if gesture:
                    print(f"检测到手势：{gesture}")
                    if gesture in self.actions:
                        for action in self.actions[gesture]:
                            action.execute(gesture)
                    
                    # 触发外部回调
                    if self.on_gesture_detected:
                        self.on_gesture_detected(gesture)
                
                # 绘制状态提示
                if gesture:
                    cv2.putText(
                        processed_frame,
                        f"Gesture: {gesture}",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 255, 0),
                        3
                    )
                else:
                    cv2.putText(
                        processed_frame,
                        "Waiting for gesture...",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2
                    )
                
                cv2.imshow(self.config.window_name, processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("🔚 退出程序")
                    self.running = False
        
        finally:
            self.release_resources()

    def release_resources(self):
        """释放资源"""
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        cv2.destroyAllWindows()

# ---------------------- 示例扩展 ----------------------
class VoiceFeedbackAction(GestureAction):
    """语音反馈动作（示例）"""
    def execute(self, gesture: str) -> None:
        # 实际应用中可以集成TTS语音合成
        print(f"语音提示：检测到{gesture}手势")

class LogAction(GestureAction):
    """日志记录动作（示例）"""
    def execute(self, gesture: str) -> None:
        import datetime
        print(f"[{datetime.datetime.now()}] 记录手势: {gesture}")

# ---------------------- 主程序入口 ----------------------
def main():
    config = GestureConfig()
    detector = HandGestureDetector(config)
    
    # 注册自定义动作
    detector.register_action("ok", VoiceFeedbackAction())
    detector.register_action("7", LogAction())
    
    detector.init_mediapipe()
    if not detector.init_camera():
        return
    
    detector.run_detection()

if __name__ == "__main__":
    main()