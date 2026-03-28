"""
游戏键盘控制模块
使用 pyautogui 实现键盘输入控制
"""

import time
import pyautogui


class GameController:
    """游戏键盘控制类"""

    # 东方Project 标准按键映射
    KEY_UP = 'up'
    KEY_DOWN = 'down'
    KEY_LEFT = 'left'
    KEY_RIGHT = 'right'
    KEY_SHOOT = 'z'        # 射击
    KEY_BOMB = 'x'         # Bomb
    KEY_SLOW = 'shift'     # 低速移动
    KEY_SKIP = 'ctrl'      # 跳过对话
    KEY_PAUSE = 'escape'   # 暂停

    def __init__(self, key_delay=0.01):
        """
        初始化游戏控制器

        Args:
            key_delay: 按键延迟时间（秒），用于控制输入速度
        """
        self.key_delay = key_delay

        # 当前按下的按键集合
        self.pressed_keys = set()

        # 禁用 pyautogui 的安全检查（提高性能）
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

    def press_key(self, key):
        """
        按下一个按键

        Args:
            key: 按键名称
        """
        if key not in self.pressed_keys:
            pyautogui.keyDown(key)
            self.pressed_keys.add(key)
            time.sleep(self.key_delay)

    def release_key(self, key):
        """
        释放一个按键

        Args:
            key: 按键名称
        """
        if key in self.pressed_keys:
            pyautogui.keyUp(key)
            self.pressed_keys.discard(key)
            time.sleep(self.key_delay)

    def tap_key(self, key, duration=0.05):
        """
        点击一个按键（按下后立即释放）

        Args:
            key: 按键名称
            duration: 按键持续时间（秒）
        """
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def release_all_keys(self):
        """释放所有当前按下的按键"""
        for key in list(self.pressed_keys):
            pyautogui.keyUp(key)
        self.pressed_keys.clear()

    def move(self, direction, slow=False):
        """
        移动自机

        Args:
            direction: 方向 ('up', 'down', 'left', 'right', 或组合如 'up-left')
            slow: 是否低速移动
        """
        # 先释放所有方向键
        self.release_key(self.KEY_UP)
        self.release_key(self.KEY_DOWN)
        self.release_key(self.KEY_LEFT)
        self.release_key(self.KEY_RIGHT)

        # 处理组合方向
        directions = direction.split('-')
        for d in directions:
            if d in ['up', 'down', 'left', 'right']:
                self.press_key(d)

        # 处理低速移动
        if slow:
            self.press_key(self.KEY_SLOW)
        else:
            self.release_key(self.KEY_SLOW)

    def shoot(self, enable=True):
        """
        控制射击

        Args:
            enable: True为开始射击，False为停止射击
        """
        if enable:
            self.press_key(self.KEY_SHOOT)
        else:
            self.release_key(self.KEY_SHOOT)

    def bomb(self):
        """使用Bomb（点击一次）"""
        self.tap_key(self.KEY_BOMB, duration=0.1)

    def execute_action(self, action_code):
        """
        执行动作编码

        Args:
            action_code: 动作编码（整数或字符串）
                整数编码示例：
                0: 无操作
                1: 上
                2: 下
                3: 左
                4: 右
                5: 上-左
                6: 上-右
                7: 下-左
                8: 下-右
                9: Bomb

        Returns:
            str: 执行的动作描述
        """
        # 先释放所有按键
        self.release_all_keys()

        # 默认持续射击
        self.press_key(self.KEY_SHOOT)

        # 动作映射
        action_map = {
            0: ('none', None),
            1: ('up', self.KEY_UP),
            2: ('down', self.KEY_DOWN),
            3: ('left', self.KEY_LEFT),
            4: ('right', self.KEY_RIGHT),
            5: ('up-left', [self.KEY_UP, self.KEY_LEFT]),
            6: ('up-right', [self.KEY_UP, self.KEY_RIGHT]),
            7: ('down-left', [self.KEY_DOWN, self.KEY_LEFT]),
            8: ('down-right', [self.KEY_DOWN, self.KEY_RIGHT]),
            9: ('bomb', 'bomb'),
        }

        if action_code in action_map:
            action_name, keys = action_map[action_code]

            if keys == 'bomb':
                self.bomb()
            elif keys is not None:
                if isinstance(keys, list):
                    for key in keys:
                        self.press_key(key)
                else:
                    self.press_key(keys)

            return action_name
        else:
            return 'unknown'

    def execute_multi_key_action(self, up=False, down=False, left=False, right=False,
                                  shoot=True, slow=False, bomb=False):
        """
        执行多按键组合动作

        Args:
            up, down, left, right: 方向键状态
            shoot: 是否射击
            slow: 是否低速移动
            bomb: 是否使用Bomb
        """
        # 方向键
        if up:
            self.press_key(self.KEY_UP)
        else:
            self.release_key(self.KEY_UP)

        if down:
            self.press_key(self.KEY_DOWN)
        else:
            self.release_key(self.KEY_DOWN)

        if left:
            self.press_key(self.KEY_LEFT)
        else:
            self.release_key(self.KEY_LEFT)

        if right:
            self.press_key(self.KEY_RIGHT)
        else:
            self.release_key(self.KEY_RIGHT)

        # 射击
        if shoot:
            self.press_key(self.KEY_SHOOT)
        else:
            self.release_key(self.KEY_SHOOT)

        # 低速移动
        if slow:
            self.press_key(self.KEY_SLOW)
        else:
            self.release_key(self.KEY_SLOW)

        # Bomb
        if bomb:
            self.tap_key(self.KEY_BOMB)

    def reset(self):
        """重置控制器状态（释放所有按键）"""
        self.release_all_keys()
