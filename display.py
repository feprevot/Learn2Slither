import sys
import time
from constants import BOARD_SIZE

CELL_SIZE = 60
MARGIN = 2
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE

COLOR_BG         = (30, 30, 30)
COLOR_GRID       = (45, 45, 45)
COLOR_SNAKE_HEAD = (50, 120, 255)
COLOR_SNAKE_BODY = (30, 80, 200)
COLOR_GREEN      = (60, 200, 80)
COLOR_RED        = (220, 50, 50)
COLOR_TEXT       = (220, 220, 220)


class Display:
    def __init__(self, visual=True, speed=0.2, step_by_step=False):
        self.visual = visual
        self.speed = speed
        self.step_by_step = step_by_step
        self.screen = None

        if self.visual:
            import pygame
            self.pygame = pygame
            pygame.init()
            self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
            pygame.display.set_caption("Learn2Slither")
            self.font = pygame.font.SysFont("monospace", 18)
            self.clock = pygame.time.Clock()

    def render(self, board):
        if not self.visual:
            return
        pg = self.pygame
        self.screen.fill(COLOR_BG)

        for i in range(BOARD_SIZE + 1):
            pg.draw.line(self.screen, COLOR_GRID, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE))
            pg.draw.line(self.screen, COLOR_GRID, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE))

        grid = board.get_grid()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = grid[r][c]
                x = c * CELL_SIZE + MARGIN
                y = r * CELL_SIZE + MARGIN
                size = CELL_SIZE - 2 * MARGIN
                rect = pg.Rect(x, y, size, size)
                if cell == 'H':
                    pg.draw.rect(self.screen, COLOR_SNAKE_HEAD, rect, border_radius=8)
                elif cell == 'S':
                    pg.draw.rect(self.screen, COLOR_SNAKE_BODY, rect, border_radius=5)
                elif cell == 'G':
                    pg.draw.ellipse(self.screen, COLOR_GREEN, rect)
                elif cell == 'R':
                    pg.draw.ellipse(self.screen, COLOR_RED, rect)

        length_text = self.font.render(f"Length: {board.snake_length()}", True, COLOR_TEXT)
        self.screen.blit(length_text, (5, 5))

        pg.display.flip()
        self._handle_events()

    def print_vision(self, board):
        print(board.format_vision())

    def wait(self, done):
        if not self.visual:
            return
        if self.step_by_step:
            self._wait_keypress()
        else:
            time.sleep(self.speed)
            self._handle_events()

    def _handle_events(self):
        pg = self.pygame
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()
                sys.exit(0)
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.close()
                sys.exit(0)

    def _wait_keypress(self):
        pg = self.pygame
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.close()
                    sys.exit(0)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.close()
                        sys.exit(0)
                    waiting = False

    def close(self):
        if self.visual and self.screen is not None:
            self.pygame.quit()
            self.screen = None
