import math

from talon import cron
from talon.types import Point2d, Rect
from enum import Enum, unique


@unique
class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @staticmethod
    def from_str(direction: str):
        if direction == "up":
            return Direction.UP
        elif direction == "right":
            return Direction.RIGHT
        elif direction == "down":
            return Direction.DOWN
        elif direction == "left":
            return Direction.LEFT
        
        raise AttributeError(f"Unknown direction: {direction}")

    @staticmethod
    def max_value():
        return max([e.value for e in Direction])

    def next(self):
        next_value = self.value + 1
        if next_value > Direction.max_value():
            next_value = 0
        return Direction(next_value)

    def previous(self):
        previous_value = self.value - 1
        if previous_value < 0:
            previous_value = Direction.max_value()
        return Direction(previous_value)


class ActiveTheme(Enum):
    DARK = 0
    LIGHT = 1

    def from_str(theme: str):
        if theme == "dark":
            return ActiveTheme.DARK
        return ActiveTheme.LIGHT


class SnakeSegment:
    def __init__(self, rect: Rect):
        self.rect = rect

    def center(self):
        return Point2d(self.rect.x + (self.rect.width / 2),
                       self.rect.y + (self.rect.height / 2))

    def copy(self):
        return SnakeSegment(self.rect.copy())


class SnakeTheme:
    def __init__(self, head_background_color: str, head_cursor_color: str,
                 segment_background_color: str):
        self.head_background_color = head_background_color
        self.head_cursor_color = head_cursor_color
        self.segment_background_color = segment_background_color


class SnakeConfig:
    def __init__(self, dark_theme: SnakeTheme, light_theme: SnakeTheme,
                 maximum_interval: int, segment_count: int, segment_size: int,
                 segment_spacing: int):
        self.dark_theme = dark_theme
        self.light_theme = light_theme
        self.maximum_interval = maximum_interval + 1
        self.segment_count = segment_count
        self.segment_size = segment_size
        self.segment_spacing = segment_spacing


class Snake:
    def __init__(self, config: SnakeConfig, theme: ActiveTheme, start_point: Point2d,
                 start_direction: Direction, start_speed: int):
        self.config = config
        self.theme = theme
        self.direction = start_direction
        self.speed = start_speed
        self.move_job = None
        self.create_head(start_point)
        self.create_segments()

    def change_direction(self, direction: Direction, phrase_elapsed: int = None):
        here = self.get_here(phrase_elapsed)
        offset = Point2d(self.head.rect.center.x - here.x, self.head.rect.center.y - here.y)

        self.head.rect.center = Point2d(self.head.rect.center.x - offset.x, self.head.rect.center.y - offset.y)

        for segment in self.segments:
            segment.rect.center = Point2d(segment.rect.center.x - offset.x, segment.rect.center.y - offset.y)

        self.direction = direction

    def change_speed(self, speed: int):
        self.stop()
        self.speed = speed
        self.start()

    def change_theme(self, theme: ActiveTheme):
        self.theme = theme

    def create_head(self, start_point: Point2d):
        rect = Rect(start_point.x - (self.config.segment_size / 2),
                    start_point.y - (self.config.segment_size / 2),
                    self.config.segment_size, self.config.segment_size)
        self.head = SnakeSegment(rect) 

    def create_segments(self):
        self.segments = []
        for i in range(self.config.segment_count):
            offset = self.config.segment_size + self.config.segment_spacing
            x_offset = 0
            y_offset = 0
            if self.direction == Direction.UP:
                y_offset = offset
            elif self.direction == Direction.RIGHT:
                x_offset = - offset
            elif self.direction == Direction.DOWN:
                y_offset = - offset
            elif self.direction == Direction.LEFT:
                x_offset = offset

            segment_rect = Rect(self.head.rect.x + (x_offset * (i + 1)),
                                self.head.rect.y + (y_offset * (i + 1)),
                                self.config.segment_size,
                                self.config.segment_size)
            self.segments.append(SnakeSegment(segment_rect))

    def draw(self, canvas):
        theme = self.get_theme()
        paint = canvas.paint

        # draw segments
        paint.color = theme.segment_background_color
        for segment in self.segments:
            canvas.draw_rect(segment.rect)

        # draw head
        paint.color = theme.head_background_color
        canvas.draw_rect(self.head.rect)
        paint.color = theme.head_cursor_color
        cursor_rect = Rect(self.head.rect.x - 1 + ((self.head.rect.width) / 2),
                           self.head.rect.y - 1 + ((self.head.rect.width) / 2),
                           2, 2)
        canvas.draw_rect(cursor_rect)

    def get_here(self, phrase_elapsed: int = None):
        head_point = self.head.center()
        mouse_point = head_point.copy()

        if phrase_elapsed is not None and self.is_moving():
            interval = self.get_interval()
            vector = self.get_vector()

            elapsed_intervals = math.floor(phrase_elapsed / interval)
            if elapsed_intervals > 1:
                elapsed_intervals -= 1

            vector.x *= elapsed_intervals
            vector.y *= elapsed_intervals

            mouse_point = Point2d(head_point.x - vector.x, head_point.y - vector.y)

        return mouse_point

    def get_interval(self):
        return self.config.maximum_interval - self.speed

    def get_theme(self):
        if self.theme == ActiveTheme.DARK:
            return self.config.dark_theme
        return self.config.light_theme 

    def get_vector(self) -> Point2d:
        vector = Point2d(0, 0)

        if self.direction in [Direction.UP, Direction.DOWN]:
            vector.y = self.head.rect.height + self.config.segment_spacing
        else:
            vector.x = self.head.rect.width + self.config.segment_spacing

        if self.direction == Direction.UP:
            vector.y = - vector.y
        elif self.direction == Direction.LEFT:
            vector.x = - vector.x

        return vector

    def is_moving(self):
        return bool(self.move_job)

    def move(self):
        self.segments.insert(0, self.head.copy())
        self.segments.pop()

        vector = self.get_vector()
        self.head.rect.x += vector.x
        self.head.rect.y += vector.y

    def start(self):
        interval = self.get_interval()
        self.move_job = cron.interval(f"{interval}ms", self.move)

    def stop(self):
        if self.is_moving():
            cron.cancel(self.move_job)
            self.move_job = None

    def toggle(self):
        if self.move_job:
            self.stop()
        else:
            self.start()
