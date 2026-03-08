import curses
import random
import time

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(150)

    sh, sw = stdscr.getmaxyx()
    # 游戏区域
    h, w = min(24, sh - 2), min(60, sw - 2)
    offset_y = (sh - h) // 2
    offset_x = (sw - w) // 2

    # 画边框
    win = curses.newwin(h + 2, w + 2, offset_y, offset_x)
    win.keypad(True)
    win.nodelay(True)
    win.timeout(150)
    win.border()

    # 初始蛇
    snake = [(h // 2, w // 4 + i) for i in range(3, 0, -1)]
    direction = curses.KEY_RIGHT

    # 生成食物
    def new_food():
        while True:
            pos = (random.randint(1, h - 1), random.randint(1, w - 1))
            if pos not in snake:
                return pos

    food = new_food()
    win.addch(food[0], food[1], '*', curses.A_BOLD)

    score = 0

    while True:
        key = win.getch()

        # 方向控制，不允许反向
        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            opposites = {
                curses.KEY_UP: curses.KEY_DOWN,
                curses.KEY_DOWN: curses.KEY_UP,
                curses.KEY_LEFT: curses.KEY_RIGHT,
                curses.KEY_RIGHT: curses.KEY_LEFT,
            }
            if key != opposites[direction]:
                direction = key
        elif key == ord('q'):
            break

        # 计算新头部
        head = snake[0]
        if direction == curses.KEY_UP:
            new_head = (head[0] - 1, head[1])
        elif direction == curses.KEY_DOWN:
            new_head = (head[0] + 1, head[1])
        elif direction == curses.KEY_LEFT:
            new_head = (head[0], head[1] - 1)
        else:
            new_head = (head[0], head[1] + 1)

        # 碰墙或撞自身
        if (new_head[0] <= 0 or new_head[0] >= h + 1 or
                new_head[1] <= 0 or new_head[1] >= w + 1 or
                new_head in snake):
            break

        snake.insert(0, new_head)

        # 吃到食物
        if new_head == food:
            score += 10
            food = new_food()
            win.addch(food[0], food[1], '*', curses.A_BOLD)
        else:
            tail = snake.pop()
            win.addch(tail[0], tail[1], ' ')

        # 绘制蛇头和身体
        win.addch(snake[0][0], snake[0][1], '@')
        for seg in snake[1:]:
            win.addch(seg[0], seg[1], 'o')

        # 显示分数
        win.addstr(0, 2, f' Score: {score} ')
        win.refresh()

    # 游戏结束画面
    win.clear()
    win.border()
    msg = f'Game Over! Score: {score}'
    win.addstr(h // 2, (w - len(msg)) // 2 + 1, msg, curses.A_BOLD)
    win.addstr(h // 2 + 1, (w - 20) // 2 + 1, 'Press any key to exit')
    win.nodelay(False)
    win.getch()


if __name__ == '__main__':
    curses.wrapper(main)
