from talon import Context, Module, actions, canvas, ctrl, skia, ui
from talon.skia import Paint
from talon.types import Point2d
mod = Module()

mod.tag("snake_mouse_history_enabled", desc="Snake mouse history enabled.")
mod.tag("snake_mouse_history_active", desc="Snake mouse history active.")
mod.mode("snake_mouse_history", desc="Snake mouse history mode.")


setting_maximum_points = mod.setting(
    "snake_mouse_history_maximum_points",
    type=int,
    default=30,
    desc="Maximum number of points to keep."
)

setting_point_radius = mod.setting(
    "snake_mouse_history_point_radius",
    type=int,
    default=5,
    desc="History point radius."
)


ctx = Context()

ctx.matches = r"""
tag: user.snake_mouse_history_enabled
"""

# TODO(bkd): enable/disable, mode, etc.
class History:
    def __init__(self):
        self.apple_image = skia.Image.from_file("/Users/bluecamel/.talon/user/snake_mouse/apple.png")
        self.enabled = False
        self.canvas = None
        self.points = []

    def add(self, point: Point2d):
        self.points.append(point)
        self.points = self.points[- setting_maximum_points.get():]

    def clear(self):
        self.points = []

    def disable(self):
        if not self.enabled:
            return

        actions.mode.disable("user.snake_mouse_history")
        actions.mode.enable("command")

        self.enabled = False

        if self.canvas:
            self.canvas.close()
            self.canvas = None

    def draw(self, canvas):
        canvas.paint.color = "ff0000"
        canvas.paint.text_align = canvas.paint.TextAlign.CENTER

        text_rect = canvas.paint.measure_text("55")[1]
        text_offset = text_rect.height / 2
        for index, point in enumerate(self.points):
            canvas.paint.color = "ff0000ff"
            canvas.paint.style = Paint.Style.FILL
            canvas.draw_image(self.apple_image, point.x - self.apple_image.width / 2, point.y - 1 - self.apple_image.height / 2)
            canvas.paint.color = "ffffffff"
            canvas.draw_text(str(index + 1), point.x, point.y + text_offset)

    def enable(self):
        if self.enabled:
            return

        if not self.points:
            return

        self.enabled = True

        self.screen = ui.screens()[0]
        self.canvas = canvas.Canvas.from_screen(self.screen)

        self.canvas.register("draw", self.draw)

        ctx.tags = ["user.snake_mouse_history_active"]

        actions.mode.enable("user.snake_mouse_history")
        actions.mode.disable("command")

    def select(self, index: int):
        if index <= len(self.points):
            print("index", index, "len", len(self.points))
            point = self.points[index - 1]
            ctrl.mouse_move(point.x, point.y)
            self.disable()

snake_mouse_history = History()

@mod.action_class
class Actions:
    def snake_mouse_history_clear():
        """Clear snake mouse history."""
        snake_mouse_history.clear()

    def snake_mouse_history_disable():
        """Disable snake mouse history."""
        snake_mouse_history.disable()

    def snake_mouse_history_enable():
        """Enable snake mouse history."""
        snake_mouse_history.enable()

    def snake_mouse_history_select(number: int):
        """Select history point."""
        snake_mouse_history.select(number)
