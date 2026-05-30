import pyautogui
import time

print("移动鼠标到目标位置，按 Ctrl+C 停止...")
try:
    while True:
        x, y = pyautogui.position()
        print(f"\r当前鼠标坐标: X={x}, Y={y}", end="")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n已停止。")
# x1 = 122
# y1 = 515
# x2 = 1286
# y2 = 1268