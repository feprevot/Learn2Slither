import random
from snake_class import Snake
from constants import (
    UP, DOWN, LEFT, RIGHT, ACTIONS, DIRECTION_VECTORS, BOARD_SIZE,
    REWARD_GREEN, REWARD_RED, REWARD_DEATH, REWARD_STEP,
)


class Board:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.green_apples = set()
        self.red_apple = None
        self._place_snake()
        self._place_apples()

    def _place_snake(self):
        """Place a 3-segment snake at a random valid position."""
        while True:
            direction = random.choice(ACTIONS)
            dr, dc = DIRECTION_VECTORS[direction]
            r = random.randint(0, self.board_size - 1)
            c = random.randint(0, self.board_size - 1)
            segments = [(r, c)]
            valid = True
            for i in range(1, 3):
                nr = r - dr * i
                nc = c - dc * i
                if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                    segments.append((nr, nc))
                else:
                    valid = False
                    break
            if valid:
                self.snake = Snake(segments)
                return

    def _empty_cells(self):
        occupied = set(self.snake.segments)
        occupied |= self.green_apples
        if self.red_apple:
            occupied.add(self.red_apple)
        return [
            (r, c)
            for r in range(self.board_size)
            for c in range(self.board_size)
            if (r, c) not in occupied
        ]

    def _place_apples(self):
        for _ in range(2):
            self._spawn_green()
        self._spawn_red()

    def _spawn_green(self):
        empty = self._empty_cells()
        if empty:
            self.green_apples.add(random.choice(empty))

    def _spawn_red(self):
        empty = self._empty_cells()
        if empty:
            self.red_apple = random.choice(empty)

    def step(self, action):
        """
        Apply action, update board state.
        Returns (reward, done).
        """
        dr, dc = DIRECTION_VECTORS[action]
        r, c = self.snake.head()
        new_head = (r + dr, c + dc)

        if not (0 <= new_head[0] < self.board_size and
                0 <= new_head[1] < self.board_size):
            return REWARD_DEATH, True

        _, tail = self.snake.move(action)

        if self.snake.head_collides_body():
            return REWARD_DEATH, True

        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self.snake.grow(tail)
            self._spawn_green()
            return REWARD_GREEN, False

        if new_head == self.red_apple:
            self.snake.shrink()
            self._spawn_red()
            if self.snake.length() == 0:
                return REWARD_RED, True
            return REWARD_RED, False
        return REWARD_STEP, False

    def get_state(self):
        """
        Per direction, encode (first_object_seen, distance_bucket).
          first_object_seen ∈ {'D' wall/body, 'G' green, 'R' red}
          distance_bucket  ∈ {1 = next cell, 2 = 2-3 cells, 3 = farther}
        """
        head = self.snake.head()
        state = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            dr, dc = DIRECTION_VECTORS[direction]
            r, c = head[0] + dr, head[1] + dc
            dist = 1
            cell = 'D'
            while 0 <= r < self.board_size and 0 <= c < self.board_size:
                if (r, c) in self.snake.segments:
                    cell = 'D'
                    break
                if (r, c) in self.green_apples:
                    cell = 'G'
                    break
                if (r, c) == self.red_apple:
                    cell = 'R'
                    break
                r += dr
                c += dc
                dist += 1
            bucket = 1 if dist == 1 else (2 if dist <= 3 else 3)
            state.append(f"{cell}{bucket}")
        return tuple(state)

    def format_vision(self):
        """Return a human-readable string of the
        snake's vision for terminal display."""
        head_r, head_c = self.snake.head()

        def cell(r, c):
            if (r, c) in self.snake.segments:
                return 'S'
            if (r, c) in self.green_apples:
                return 'G'
            if (r, c) == self.red_apple:
                return 'R'
            return '0'

        middle = ['W']
        for c in range(self.board_size):
            middle.append('H' if c == head_c else cell(head_r, c))
        middle.append('W')
        middle_line = ''.join(middle)

        top = ['W'] + [cell(r, head_c) for r in range(head_r)]
        bottom = [cell(r, head_c)
                  for r in range(head_r + 1, self.board_size)] + ['W']

        pad = ' ' * (head_c + 1)
        lines = [pad + ch for ch in top]
        lines.append(middle_line)
        lines.extend(pad + ch for ch in bottom)
        return '\n'.join(lines)

    def snake_length(self):
        return self.snake.length()

    def get_grid(self):
        """Return a 2D list of cell symbols for rendering."""
        grid = [['0'] * self.board_size for _ in range(self.board_size)]
        for pos in self.green_apples:
            grid[pos[0]][pos[1]] = 'G'
        if self.red_apple:
            grid[self.red_apple[0]][self.red_apple[1]] = 'R'
        for seg in self.snake.body():
            grid[seg[0]][seg[1]] = 'S'
        r, c = self.snake.head()
        grid[r][c] = 'H'
        return grid
