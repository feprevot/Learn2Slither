import random
from snake_class import Snake
from constants import (
    UP, DOWN, LEFT, RIGHT, ACTIONS, DIRECTION_VECTORS, BOARD_SIZE,
    REWARD_GREEN, REWARD_RED, REWARD_DEATH, REWARD_STEP,
    THREAT_DANGER, THREAT_GREEN, THREAT_RED,
    DIST_NEAR, DIST_MEDIUM, DIST_FAR,
    CELL_EMPTY, CELL_HEAD, CELL_BODY, CELL_GREEN, CELL_RED, CELL_WALL,
)


class Board:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.green_apples = set()
        self.red_apple = None
        self.place_snake()
        self.place_apples()

    def place_snake(self):
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

    def empty_cells(self):
        """Return every (row, col) on the board that is free
        (no snake segment, no green apple, no red apple)."""
        occupied = set(self.snake.segments)
        occupied.update(self.green_apples)
        if self.red_apple:
            occupied.add(self.red_apple)

        empty = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in occupied:
                    empty.append((r, c))
        return empty

    def place_apples(self):
        for _ in range(2):
            self.spawn_green()
        self.spawn_red()

    def spawn_green(self):
        empty = self.empty_cells()
        if empty:
            self.green_apples.add(random.choice(empty))

    def spawn_red(self):
        empty = self.empty_cells()
        if empty:
            self.red_apple = random.choice(empty)

    def step(self, action):
        """
        Apply action, update board state.
        Returns (reward, done).
        """
        delta_r, delta_c = DIRECTION_VECTORS[action]
        r, c = self.snake.head()
        new_head = (r + delta_r, c + delta_c)

        if not (0 <= new_head[0] < self.board_size and
                0 <= new_head[1] < self.board_size):
            return REWARD_DEATH, True

        _, tail = self.snake.move(action)

        if self.snake.head_collides_body():
            return REWARD_DEATH, True

        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self.snake.grow(tail)
            self.spawn_green()
            return REWARD_GREEN, False

        if new_head == self.red_apple:
            self.snake.shrink()
            self.spawn_red()
            if self.snake.length() == 0:
                return REWARD_RED, True
            return REWARD_RED, False
        return REWARD_STEP, False

    def scan_direction(self, head, dr, dc):
        """
        Walk one step at a time from the head in (dr, dc) until the first
        non-empty cell or a wall. Returns (threat, distancebucket).
        """
        r, c = head[0] + dr, head[1] + dc
        distance = 1
        while 0 <= r < self.board_size and 0 <= c < self.board_size:
            if (r, c) in self.snake.segments:
                return THREAT_DANGER, self.bucket(distance)
            if (r, c) in self.green_apples:
                return THREAT_GREEN, self.bucket(distance)
            if (r, c) == self.red_apple:
                return THREAT_RED, self.bucket(distance)
            r += dr
            c += dc
            distance += 1
        return THREAT_DANGER, self.bucket(distance)

    def bucket(self, distance):
        if distance == 1:
            return DIST_NEAR
        if distance <= 3:
            return DIST_MEDIUM
        return DIST_FAR

    def get_state(self):
        """
        State = one (threat, distance) pair per direction, in (UP, DOWN,
        LEFT, RIGHT) order. Used as a hashable Q-table key.
        """
        head = self.snake.head()
        return tuple(
            self.scan_direction(head, *DIRECTION_VECTORS[direction])
            for direction in (UP, DOWN, LEFT, RIGHT)
        )

    def cell_symbols(self):
        """
        Map every occupied cell to its display symbol in one pass.
        The head is written last so it always overrides a body segment.
        """
        symbols = {pos: CELL_GREEN for pos in self.green_apples}
        if self.red_apple:
            symbols[self.red_apple] = CELL_RED
        for seg in self.snake.body():
            symbols[seg] = CELL_BODY
        symbols[self.snake.head()] = CELL_HEAD
        return symbols

    def format_vision(self):
        """Return a human-readable string of the
        snake's vision for terminal display."""
        head_r, head_c = self.snake.head()
        symbols = self.cell_symbols()

        def col(r, c):
            return symbols.get((r, c), CELL_EMPTY)

        middle = (
            CELL_WALL
            + ''.join(col(head_r, c) for c in range(self.board_size))
            + CELL_WALL
        )

        pad = ' ' * (head_c + 1)
        top = [pad + CELL_WALL] + [
            pad + col(r, head_c) for r in range(head_r)
        ]
        bottom = [
            pad + col(r, head_c)
            for r in range(head_r + 1, self.board_size)
        ] + [pad + CELL_WALL]

        return '\n'.join(top + [middle] + bottom)

    def snake_length(self):
        return self.snake.length()

    def get_grid(self):
        """Return a 2D grid (list of rows) where each cell holds the
        display symbol of what occupies it: 'H' (head), 'S' (body),
        'G' (green apple), 'R' (red apple), or '0' (empty)."""
        symbols = self.cell_symbols()

        grid = []
        for r in range(self.board_size):
            row = []
            for c in range(self.board_size):
                symbol = symbols.get((r, c), CELL_EMPTY)
                row.append(symbol)
            grid.append(row)
        return grid
