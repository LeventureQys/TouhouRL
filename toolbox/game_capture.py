"""
游戏屏幕捕获模块
使用 mss 库实现高性能屏幕截图
"""

import time
import numpy as np
from mss import mss
from PIL import Image
import cv2


class GameCapture:
    """游戏屏幕捕获类"""

    def __init__(self, window_title=None, monitor_id=1):
        """
        初始化屏幕捕获器

        Args:
            window_title: 游戏窗口标题（可选，用于自动定位）
            monitor_id: 显示器ID，默认为1（主显示器）
        """
        self.sct = mss()
        self.monitor_id = monitor_id
        self.window_title = window_title

        # 游戏区域坐标 (left, top, width, height)
        self.game_region = None

        # 性能统计
        self.frame_count = 0
        self.start_time = None

    def set_game_region(self, left, top, width, height):
        """
        手动设置游戏区域

        Args:
            left: 左上角X坐标
            top: 左上角Y坐标
            width: 区域宽度
            height: 区域高度
        """
        self.game_region = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        print(f"游戏区域已设置: {self.game_region}")

    def auto_detect_window(self):
        """
        自动检测游戏窗口位置（需要额外的窗口管理库）
        目前返回全屏区域
        """
        monitor = self.sct.monitors[self.monitor_id]
        self.game_region = {
            "left": monitor["left"],
            "top": monitor["top"],
            "width": monitor["width"],
            "height": monitor["height"]
        }
        print(f"使用显示器 {self.monitor_id}: {self.game_region}")
        return self.game_region

    def capture_frame(self, as_numpy=True):
        """
        捕获一帧画面

        Args:
            as_numpy: 是否返回numpy数组，否则返回PIL Image

        Returns:
            numpy.ndarray 或 PIL.Image: 捕获的画面
        """
        if self.game_region is None:
            self.auto_detect_window()

        # 使用 mss 捕获屏幕
        screenshot = self.sct.grab(self.game_region)

        # 转换为 PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        if as_numpy:
            # 转换为 numpy 数组 (OpenCV 格式: BGR)
            return np.array(img)[:, :, ::-1]  # RGB -> BGR
        else:
            return img

    def capture_frame_cv2(self):
        """
        捕获一帧并返回 OpenCV 格式的图像 (BGR)

        Returns:
            numpy.ndarray: BGR格式的图像数组
        """
        return self.capture_frame(as_numpy=True)

    def start_fps_counter(self):
        """开始FPS计数"""
        self.frame_count = 0
        self.start_time = time.time()

    def get_fps(self):
        """
        获取当前FPS

        Returns:
            float: 当前帧率
        """
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return self.frame_count / elapsed
        return 0.0

    def update_fps_counter(self):
        """更新FPS计数器"""
        self.frame_count += 1

    def crop_game_area(self, frame, x, y, width, height):
        """
        从捕获的画面中裁剪游戏有效区域

        Args:
            frame: 原始画面
            x, y: 裁剪起始坐标
            width, height: 裁剪尺寸

        Returns:
            numpy.ndarray: 裁剪后的图像
        """
        return frame[y:y+height, x:x+width]

    def resize_frame(self, frame, width, height):
        """
        调整画面尺寸

        Args:
            frame: 原始画面
            width, height: 目标尺寸

        Returns:
            numpy.ndarray: 调整后的图像
        """
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

    def preprocess_frame(self, frame, target_size=None, grayscale=False):
        """
        预处理画面（用于神经网络输入）

        Args:
            frame: 原始画面
            target_size: 目标尺寸 (width, height)，None表示不调整
            grayscale: 是否转换为灰度图

        Returns:
            numpy.ndarray: 预处理后的图像
        """
        processed = frame.copy()

        # 转换为灰度图
        if grayscale:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

        # 调整尺寸
        if target_size is not None:
            processed = cv2.resize(processed, target_size, interpolation=cv2.INTER_LINEAR)

        # 归一化到 [0, 1]
        processed = processed.astype(np.float32) / 255.0

        return processed

    def close(self):
        """关闭捕获器"""
        self.sct.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
