# TouhouRL Toolbox - 基础交互工具包

提供屏幕捕获和键盘控制功能，用于与东方Project游戏进行交互。

本项目目前运行于python 3.11

```bash
conda create -n THRL python=3.11 

conda activate THRL
```

## 功能特性

### 1. 屏幕捕获 (GameCapture)
- 使用 `mss` 库实现高性能屏幕截图（目标：60 FPS）
- 支持自动检测游戏窗口或手动设置捕获区域
- 提供图像预处理功能（缩放、灰度化、归一化）
- 内置 FPS 计数器用于性能监控

### 2. 键盘控制 (GameController)
- 使用 `pyautogui` 实现键盘输入控制
- 支持东方Project标准按键映射
- 提供简单的动作编码接口
- 支持多按键组合控制

## 安装依赖

```bash
pip install mss pyautogui pillow opencv-python numpy
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 快速开始

### 屏幕捕获示例

```python
from toolbox import GameCapture

# 创建捕获器
with GameCapture() as capture:
    # 自动检测窗口（使用主显示器）
    capture.auto_detect_window()

    # 或手动设置游戏区域
    # capture.set_game_region(left=100, top=100, width=640, height=480)

    # 捕获一帧
    frame = capture.capture_frame_cv2()  # 返回 OpenCV 格式 (BGR)

    # 预处理（用于神经网络）
    processed = capture.preprocess_frame(frame, target_size=(84, 84), grayscale=True)
```

### 键盘控制示例

```python
from toolbox import GameController
import time

# 创建控制器
controller = GameController()

# 方向移动
controller.move('up')           # 向上
controller.move('up-left')      # 左上
controller.move('down', slow=True)  # 低速向下

# 射击控制
controller.shoot(True)   # 开始射击
time.sleep(1)
controller.shoot(False)  # 停止射击

# 使用 Bomb
controller.bomb()

# 执行动作编码（用于强化学习）
controller.execute_action(1)  # 向上移动
controller.execute_action(5)  # 左上移动
controller.execute_action(9)  # 使用Bomb

# 重置（释放所有按键）
controller.reset()
```

### 组合使用示例

```python
from toolbox import GameCapture, GameController
import cv2

with GameCapture() as capture:
    capture.auto_detect_window()
    controller = GameController()

    # 游戏循环
    while True:
        # 捕获当前画面
        frame = capture.capture_frame_cv2()

        # 这里可以添加视觉识别逻辑
        # ...

        # 根据识别结果执行动作
        controller.execute_action(1)  # 向上移动

        # 显示画面
        cv2.imshow('Game', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    controller.reset()
    cv2.destroyAllWindows()
```

## API 文档

### GameCapture 类

#### 初始化
```python
GameCapture(window_title=None, monitor_id=1)
```
- `window_title`: 游戏窗口标题（可选）
- `monitor_id`: 显示器ID，默认为1（主显示器）

#### 主要方法

- `set_game_region(left, top, width, height)` - 手动设置游戏区域
- `auto_detect_window()` - 自动检测游戏窗口
- `capture_frame(as_numpy=True)` - 捕获一帧画面
- `capture_frame_cv2()` - 捕获一帧（OpenCV格式）
- `preprocess_frame(frame, target_size=None, grayscale=False)` - 预处理画面
- `crop_game_area(frame, x, y, width, height)` - 裁剪游戏区域
- `resize_frame(frame, width, height)` - 调整画面尺寸
- `get_fps()` - 获取当前FPS
- `start_fps_counter()` - 开始FPS计数
- `update_fps_counter()` - 更新FPS计数器

### GameController 类

#### 初始化
```python
GameController(key_delay=0.01)
```
- `key_delay`: 按键延迟时间（秒）

#### 按键常量
- `KEY_UP`, `KEY_DOWN`, `KEY_LEFT`, `KEY_RIGHT` - 方向键
- `KEY_SHOOT` - 射击键 (Z)
- `KEY_BOMB` - Bomb键 (X)
- `KEY_SLOW` - 低速移动键 (Shift)
- `KEY_PAUSE` - 暂停键 (ESC)

#### 主要方法

- `press_key(key)` - 按下按键
- `release_key(key)` - 释放按键
- `tap_key(key, duration=0.05)` - 点击按键
- `release_all_keys()` - 释放所有按键
- `move(direction, slow=False)` - 移动自机
- `shoot(enable=True)` - 控制射击
- `bomb()` - 使用Bomb
- `execute_action(action_code)` - 执行动作编码
- `execute_multi_key_action(...)` - 执行多按键组合
- `reset()` - 重置控制器状态

#### 动作编码

| 编码 | 动作 |
|------|------|
| 0 | 无操作 |
| 1 | 向上 |
| 2 | 向下 |
| 3 | 向左 |
| 4 | 向右 |
| 5 | 左上 |
| 6 | 右上 |
| 7 | 左下 |
| 8 | 右下 |
| 9 | Bomb |

## 测试

运行测试脚本：

```bash
cd toolbox
python test_toolbox.py
```

测试项目包括：
1. 屏幕捕获测试 - 实时显示捕获画面和FPS
2. 键盘控制测试 - 测试各种按键操作
3. 组合功能测试 - 同时测试捕获和控制
4. FPS性能基准测试 - 测试不同分辨率下的性能

## 性能优化建议

1. **手动设置游戏区域**：使用 `set_game_region()` 而不是捕获整个屏幕
2. **降低分辨率**：使用 `resize_frame()` 降低图像尺寸
3. **减少预处理**：只在必要时进行灰度化和归一化
4. **调整按键延迟**：根据游戏响应速度调整 `key_delay` 参数

## 注意事项

1. 使用键盘控制前，确保游戏窗口处于激活状态
2. 某些游戏可能需要管理员权限才能接收键盘输入
3. 建议在窗口模式下运行游戏以便于调试
4. 捕获性能受显示器分辨率和游戏窗口大小影响

## 下一步

- 实现游戏元素检测（自机、子弹、敌机、道具）
- 添加OCR数值识别（残机、Bomb、得分）
- 实现轨迹预测和危险度评估
- 构建强化学习环境接口
