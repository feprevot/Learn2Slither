from constants import DIRECTION_VECTORS


class Snake:
    def __init__(self, segments):
        self.segments = list(segments)

    def head(self):
        return self.segments[0]

    def body(self):
        return self.segments[1:]

    def length(self):
        return len(self.segments)

    def move(self, action):
        delta_r, delta_c = DIRECTION_VECTORS[action]
        r, c = self.head()
        new_head = (r + delta_r, c + delta_c)
        self.segments.insert(0, new_head)
        tail = self.segments.pop()
        return new_head, tail

    def grow(self, tail):
        self.segments.append(tail)

    def shrink(self):
        if self.segments:
            self.segments.pop()

    def head_collides_body(self):
        return self.head() in self.segments[1:]
