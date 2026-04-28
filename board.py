import random
from snake import Snake
from constants import (
    UP, DOWN, LEFT, RIGHT, ACTIONS, DIRECTION_VECTORS, BOARD_SIZE,
    REWARD_GREEN, REWARD_RED, REWARD_DEATH, REWARD_STEP,
)


class Board:
    def __init__(self):
        self.green_apples = set()
        self.red_apple = None
        self._place_snake()
        self._place_apples()

    # ------------------------------------------------------------------ setup

    def _place_snake(self):
        """Place a 3-segment snake at a random valid position."""
        while True:
            direction = random.choice(ACTIONS)
            dr, dc = DIRECTION_VECTORS[direction]
            r = random.randint(0, BOARD_SIZE - 1)
            c = random.randint(0, BOARD_SIZE - 1)
            segments = [(r, c)]
            valid = True
            for i in range(1, 3):
                nr = r - dr * i   # body extends opposite to movement direction
                nc = c - dc * i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
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
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
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

    # ------------------------------------------------------------------ step

    def step(self, action):
        """
        Apply action, update board state.
        Returns (reward, done).
        """
        dr, dc = DIRECTION_VECTORS[action]
        r, c = self.snake.head()
        new_head = (r + dr, c + dc)

        # Wall collision
        if not (0 <= new_head[0] < BOARD_SIZE and 0 <= new_head[1] < BOARD_SIZE):
            return REWARD_DEATH, True

        _, tail = self.snake.move(action)

        # Self collision
        if self.snake.head_collides_body():
            return REWARD_DEATH, True

        # Apple collisions
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

    # ------------------------------------------------------------------ state

    def get_state(self):
        """
        Compact state: for each direction (UP, DOWN, LEFT, RIGHT) return
        the first relevant object seen from the head:
          'D' = danger (wall or body segment)
          'G' = green apple
          'R' = red apple
          '0' = nothing before the wall
        State space: 4^4 = 256 states → high revisit rate, fast Q-value convergence.
        """
        head = self.snake.head()
        state = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            dr, dc = DIRECTION_VECTORS[direction]
            r, c = head[0] + dr, head[1] + dc
            cell = '0'
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if (r, c) in self.snake.segments:
                    cell = 'D'
                    break
                elif (r, c) in self.green_apples:
                    cell = 'G'
                    break
                elif (r, c) == self.red_apple:
                    cell = 'R'
                    break
                r += dr
                c += dc
            else:
                cell = 'D'  # hit the wall
            state.append(cell)
        return tuple(state)

    def format_vision(self):
        """Return a human-readable string of the snake's vision for terminal display."""
        head = self.snake.head()
        lines = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            dr, dc = DIRECTION_VECTORS[direction]
            vision = []
            r, c = head[0] + dr, head[1] + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if (r, c) in self.snake.segments:
                    vision.append('S')
                elif (r, c) in self.green_apples:
                    vision.append('G')
                elif (r, c) == self.red_apple:
                    vision.append('R')
                else:
                    vision.append('0')
                r += dr
                c += dc
            vision.append('W')

            # Display: head at the junction, direction label
            if direction in (DOWN, RIGHT):
                sequence = ['H'] + vision
            else:
                sequence = list(reversed(vision)) + ['H']
            lines.append(f"{direction:5}: {' '.join(sequence)}")
        return '\n'.join(lines)

    # ------------------------------------------------------------------ utils

    def snake_length(self):
        return self.snake.length()

    def get_grid(self):
        """Return a 2D list of cell symbols for rendering."""
        grid = [['0'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        for pos in self.green_apples:
            grid[pos[0]][pos[1]] = 'G'
        if self.red_apple:
            grid[self.red_apple[0]][self.red_apple[1]] = 'R'
        for seg in self.snake.body():
            grid[seg[0]][seg[1]] = 'S'
        r, c = self.snake.head()
        grid[r][c] = 'H'
        return grid
