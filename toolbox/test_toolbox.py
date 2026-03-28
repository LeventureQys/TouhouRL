"""
基础交互系统测试脚本
测试屏幕捕获和键盘控制功能
"""

import time
import cv2
import numpy as np
from game_capture import GameCapture
from game_controller import GameController


def test_screen_capture():
    """测试屏幕捕获功能"""
    print("=" * 50)
    print("测试屏幕捕获功能")
    print("=" * 50)

    with GameCapture() as capture:
        # 自动检测窗口
        capture.auto_detect_window()

        # 开始FPS计数
        capture.start_fps_counter()

        print("\n开始捕获画面，按 'q' 键退出...")
        print("提示：你可以手动设置游戏区域以提高性能")

        frame_count = 0
        start_time = time.time()

        while True:
            # 捕获一帧
            frame = capture.capture_frame_cv2()
            capture.update_fps_counter()

            # 显示FPS
            fps = capture.get_fps()
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 显示画面
            cv2.imshow('Screen Capture Test', frame)

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1

            # 每100帧输出一次统计
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                avg_fps = frame_count / elapsed
                print(f"已捕获 {frame_count} 帧，平均FPS: {avg_fps:.1f}")

        cv2.destroyAllWindows()
        print(f"\n测试完成！总共捕获 {frame_count} 帧")


def test_keyboard_control():
    """测试键盘控制功能"""
    print("\n" + "=" * 50)
    print("测试键盘控制功能")
    print("=" * 50)

    controller = GameController()

    print("\n将在3秒后开始测试键盘控制...")
    print("请确保游戏窗口处于激活状态！")
    time.sleep(3)

    print("\n测试1: 方向键移动")
    directions = ['up', 'down', 'left', 'right', 'up-left', 'up-right', 'down-left', 'down-right']
    for direction in directions:
        print(f"  移动方向: {direction}")
        controller.move(direction)
        time.sleep(0.5)

    controller.release_all_keys()
    time.sleep(0.5)

    print("\n测试2: 射击控制")
    print("  开始射击")
    controller.shoot(True)
    time.sleep(1)
    print("  停止射击")
    controller.shoot(False)
    time.sleep(0.5)

    print("\n测试3: 低速移动")
    print("  低速向上移动")
    controller.move('up', slow=True)
    time.sleep(1)
    controller.release_all_keys()
    time.sleep(0.5)

    print("\n测试4: Bomb")
    print("  使用Bomb")
    controller.bomb()
    time.sleep(0.5)

    print("\n测试5: 动作编码执行")
    actions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    for action in actions:
        action_name = controller.execute_action(action)
        print(f"  执行动作 {action}: {action_name}")
        time.sleep(0.3)

    controller.reset()
    print("\n键盘控制测试完成！")


def test_combined():
    """测试组合功能：边捕获边控制"""
    print("\n" + "=" * 50)
    print("测试组合功能")
    print("=" * 50)

    print("\n将在3秒后开始...")
    print("程序会自动执行一系列动作，同时显示捕获的画面")
    print("按 'q' 键可以提前退出")
    time.sleep(3)

    with GameCapture() as capture:
        capture.auto_detect_window()
        controller = GameController()

        # 测试序列
        test_sequence = [
            (1, "向上移动"),
            (2, "向下移动"),
            (3, "向左移动"),
            (4, "向右移动"),
            (5, "左上移动"),
            (6, "右上移动"),
            (7, "左下移动"),
            (8, "右下移动"),
            (0, "停止移动"),
        ]

        for action_code, description in test_sequence:
            print(f"执行: {description}")

            # 执行动作
            controller.execute_action(action_code)

            # 捕获并显示画面（持续0.5秒）
            start = time.time()
            while time.time() - start < 0.5:
                frame = capture.capture_frame_cv2()

                # 在画面上显示当前动作
                cv2.putText(frame, description, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow('Combined Test', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        controller.reset()
        cv2.destroyAllWindows()
        print("\n组合测试完成！")


def test_fps_benchmark():
    """FPS性能基准测试"""
    print("\n" + "=" * 50)
    print("FPS性能基准测试")
    print("=" * 50)

    with GameCapture() as capture:
        capture.auto_detect_window()

        print("\n测试不同分辨率下的捕获性能...")

        test_configs = [
            (None, "原始分辨率"),
            ((640, 480), "640x480"),
            ((800, 600), "800x600"),
            ((1280, 720), "1280x720"),
        ]

        for target_size, desc in test_configs:
            print(f"\n测试配置: {desc}")

            frame_count = 0
            start_time = time.time()
            test_duration = 3.0  # 测试3秒

            while time.time() - start_time < test_duration:
                frame = capture.capture_frame_cv2()

                if target_size:
                    frame = capture.resize_frame(frame, target_size[0], target_size[1])

                frame_count += 1

            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"  捕获帧数: {frame_count}")
            print(f"  平均FPS: {fps:.1f}")
            print(f"  帧时间: {1000/fps:.2f} ms")


def main():
    """主测试函数"""
    print("TouhouRL 基础交互系统测试")
    print("=" * 50)

    while True:
        print("\n请选择测试项目：")
        print("1. 测试屏幕捕获")
        print("2. 测试键盘控制")
        print("3. 测试组合功能")
        print("4. FPS性能基准测试")
        print("0. 退出")

        choice = input("\n请输入选项 (0-4): ").strip()

        if choice == '1':
            test_screen_capture()
        elif choice == '2':
            test_keyboard_control()
        elif choice == '3':
            test_combined()
        elif choice == '4':
            test_fps_benchmark()
        elif choice == '0':
            print("\n退出测试程序")
            break
        else:
            print("\n无效选项，请重新选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
