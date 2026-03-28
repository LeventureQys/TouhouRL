"""
TouhouRL Toolbox - 基础交互工具包
提供屏幕捕获和键盘控制功能
"""

from .game_capture import GameCapture
from .game_controller import GameController

__all__ = ['GameCapture', 'GameController']
