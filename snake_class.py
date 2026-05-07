from constants import DIRECTION_VECTORS


class Snake:
    def __init__(self, segments):
        # segments: list of (row, col), head at index 0
        self.segments = list(segments)

    def head(self):
        return self.segments[0]

    def body(self):
        return self.segments[1:]

    def length(self):
        return len(self.segments)

    def move(self, action):
        """Move the snake one step. Returns (new_head, removed_tail)."""
        delta_r, delta_c = DIRECTION_VECTORS[action]
        r, c = self.head()
        new_head = (r + delta_r, c + delta_c)
        self.segments.insert(0, new_head)
        tail = self.segments.pop()
        return new_head, tail

    def grow(self, tail):
        """Re-attach the tail removed by move() (snake ate a green apple)."""
        self.segments.append(tail)

    def shrink(self):
        """Remove one extra segment from the tail (snake ate a red apple)."""
        if self.segments:
            self.segments.pop()

    def head_collides_body(self):
        """Check if the head collides with the body."""
        return self.head() in self.segments[1:]
