# 用强化学习让 AI 自己玩贪吃蛇

> 注意：这里用的是**强化学习（Reinforcement Learning, RL）**，不是严格意义上的"自监督学习"。
> 自监督学习通常指用数据本身构造监督信号（如 BERT、MAE），而让 AI 玩游戏的范式是强化学习。
> 两者都不需要人工标注，所以容易混淆——但本质上是 RL。

---

## 整体思路

```
游戏环境  ──状态 s──►  Agent（神经网络）──动作 a──►  游戏环境
    ▲                                                    │
    └──────────────── 奖励 r + 新状态 s' ◄──────────────┘
```

Agent 每一步观察游戏状态，输出一个动作（上/下/左/右），
游戏返回新状态和奖励，Agent 用这个信号更新自己的网络权重。
反复循环，Agent 逐渐学会得高分。

---

## 项目结构

```
First Game/
├── The Game/
│   └── snake.py          # 原始命令行游戏（人类玩）
├── RL/
│   ├── env.py            # 游戏环境（去掉 curses，纯逻辑）
│   ├── model.py          # 神经网络定义
│   ├── agent.py          # DQN Agent（决策 + 记忆 + 训练）
│   ├── train.py          # 训练主循环
│   └── play.py           # 加载训练好的模型，可视化观看
├── RL_GUIDE.md           # 本文档
└── requirements.txt      # 依赖
```

---

## 第一步：改造游戏环境 `env.py`

原来的 `snake.py` 依赖 `curses` 渲染，AI 训练时不需要画面，
需要一个**纯逻辑的环境**，对外暴露三个接口：

```python
env = SnakeEnv(width=20, height=20)

state = env.reset()          # 重置，返回初始状态
state, reward, done = env.step(action)  # 执行动作，返回新状态/奖励/是否结束
env.render()                 # 可选：打印到终端看效果
```

### 状态（State）设计

状态是 Agent 的"眼睛"，设计好坏直接影响学习效果。
推荐用 **11 维特征向量**（简单有效）：

| 索引 | 含义 |
|------|------|
| 0 | 当前方向正前方是否危险（墙或自身） |
| 1 | 当前方向右侧是否危险 |
| 2 | 当前方向左侧是否危险 |
| 3~6 | 当前移动方向（上/下/左/右，one-hot） |
| 7 | 食物在蛇头左边 |
| 8 | 食物在蛇头右边 |
| 9 | 食物在蛇头上方 |
| 10 | 食物在蛇头下方 |

这 11 个数字全是 0 或 1，简单清晰，网络很容易学。

### 奖励（Reward）设计

奖励信号告诉 Agent 什么行为是好的：

```
吃到食物：  +10
死亡：      -10
每步存活：  +0  （或 -0.01 鼓励快点吃食物）
```

---

## 第二步：神经网络 `model.py`

用一个简单的全连接网络（MLP）：

```
输入层：11 个神经元（对应 11 维状态）
隐藏层：256 个神经元，ReLU 激活
隐藏层：256 个神经元，ReLU 激活
输出层：3 个神经元（对应 3 个动作：直走/左转/右转）
```

为什么输出是 3 而不是 4？
因为蛇不能掉头，所以动作空间是相对方向：**直走、左转、右转**，
比绝对方向（上下左右）更容易学。

---

## 第三步：DQN Agent `agent.py`

使用经典的 **DQN（Deep Q-Network）** 算法，这是入门 RL 最常用的算法。

### 核心概念

**Q 值**：Q(s, a) 表示"在状态 s 下执行动作 a，未来能获得的总奖励期望"。
网络的目标就是准确预测每个动作的 Q 值，然后选 Q 值最大的动作。

**经验回放（Experience Replay）**：
Agent 把每一步的 `(s, a, r, s', done)` 存进一个"记忆池"，
训练时随机抽取一批来学习，打破数据的时序相关性，训练更稳定。

**ε-greedy 探索策略**：
- 以概率 ε 随机选动作（探索）
- 以概率 1-ε 选 Q 值最大的动作（利用）
- ε 从 1.0 逐渐衰减到 0.01，前期多探索，后期多利用

**目标网络（Target Network）**：
用两个结构相同的网络：主网络（实时更新）和目标网络（每隔 N 步同步一次），
防止训练目标一直变动导致不稳定。

### 训练公式（Bellman 方程）

```
目标 Q 值 = r + γ * max(Q_target(s', a'))

损失 = MSE(Q_main(s, a),  目标 Q 值)
```

- `γ`（gamma）是折扣因子，通常取 0.9，表示未来奖励打折
- 用梯度下降最小化损失，更新主网络权重

---

## 第四步：训练主循环 `train.py`

```
for episode in range(1000):          # 跑 1000 局游戏
    state = env.reset()
    while True:
        action = agent.choose_action(state)   # ε-greedy 选动作
        next_state, reward, done = env.step(action)
        agent.remember(state, action, reward, next_state, done)  # 存记忆
        agent.train_step()                    # 从记忆池采样，更新网络
        state = next_state
        if done:
            break
    agent.decay_epsilon()             # 每局结束后降低探索率
    # 每隔 N 局保存模型、打印分数
```

---

## 第五步：可视化 `play.py`

训练完成后，加载保存的模型权重，
用 `env.render()` 把游戏状态打印到终端，观察 AI 的表现。

---

## 依赖安装

```
# requirements.txt
torch>=2.0
numpy
matplotlib   # 画训练曲线用
```

```bash
conda activate TouhouSSL
pip install torch numpy matplotlib
```

---

## 预期训练效果

| 训练局数 | 平均分 | 现象 |
|----------|--------|------|
| 0~100    | <10    | 乱跑，频繁撞墙 |
| 100~500  | 10~50  | 开始朝食物走，但会绕进死角 |
| 500~2000 | 50~200 | 能稳定吃食物，偶尔死于自身 |
| 2000+    | 200+   | 表现流畅，能处理大部分情况 |

---

## 实现顺序建议

1. **先写 `env.py`**，用 `env.render()` 手动验证逻辑正确
2. **写 `model.py`**，确认输入输出维度对得上
3. **写 `agent.py`**，先只实现 `choose_action` 和 `remember`，不训练
4. **写 `train.py`**，先跑通流程（哪怕 Agent 是随机的）
5. **加入训练逻辑**，观察 loss 是否下降
6. **调参**：学习率、γ、ε 衰减速度、记忆池大小

---

## 关键超参数参考

```python
LEARNING_RATE = 0.001
GAMMA = 0.9           # 折扣因子
EPSILON_START = 1.0   # 初始探索率
EPSILON_MIN = 0.01    # 最低探索率
EPSILON_DECAY = 0.995 # 每局衰减倍率
MEMORY_SIZE = 100_000 # 经验回放池大小
BATCH_SIZE = 1000     # 每次训练采样数量
TARGET_UPDATE = 100   # 每隔多少步同步目标网络
```

---

## 下一步

文档看完后，可以让我直接帮你写每个文件的代码，
建议按顺序来：`env.py` → `model.py` → `agent.py` → `train.py` → `play.py`。
