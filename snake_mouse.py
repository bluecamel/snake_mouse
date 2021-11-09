from talon import Context, Module, actions, canvas, ctrl, ui, speech_system
from talon.types import Point2d, Rect

from .history import snake_mouse_history
from .snake import ActiveTheme, Direction, Snake, SnakeConfig, SnakeTheme


mod = Module()

mod.tag("snake_mouse_enabled", desc="Snake mouse enabled.")
mod.tag("snake_mouse_active", desc="Snake mouse active.")
mod.mode("snake_mouse", desc="Snake mouse mode.")

mod.list("snake_mouse_toggle", desc="Snake mouse toggle command.")
mod.list("snake_mouse_pause", desc="Snake mouse pause command.")
mod.list("snake_mouse_consume", desc="Snake mouse consume command.")
mod.list("snake_mouse_here", desc="Snake mouse here command.")
mod.list("snake_mouse_direction", desc="Snake mouse direction.")
mod.list("snake_mouse_start_position", desc="Snake mouse start position.")
mod.list("snake_mouse_theme", desc="Snake mouse theme.")
mod.list("snake_mouse_speed", desc="Snake mouse theme.")


setting_head_dark_background_color = mod.setting(
    "snake_mouse_head_dark_background_color",
    type=str,
    default="ffff00",
    desc="Snake head dark background color."
)

setting_head_light_background_color = mod.setting(
    "snake_mouse_head_light_background_color",
    type=str,
    default="ffff00",
    desc="Snake head light background color."
)

setting_head_dark_cursor_color = mod.setting(
    "snake_mouse_head_dark_cursor_color",
    type=str,
    default="000000",
    desc="Snake head dark cursor color."
)

setting_head_light_cursor_color = mod.setting(
    "snake_mouse_head_light_cursor_color",
    type=str,
    default="000000",
    desc="Snake head light cursor color."
)

setting_segment_dark_background_color = mod.setting(
    "snake_mouse_segment_dark_background_color",
    type=str,
    default="000000",
    desc="Snake segment dark background color."
)

setting_segment_light_background_color = mod.setting(
    "snake_mouse_segment_light_background_color",
    type=str,
    default="ffffff",
    desc="Snake segment light background color."
)

setting_segment_count = mod.setting(
    "snake_mouse_segment_count",
    type=int,
    default=10,
    desc="Snake segment count."
)

setting_segment_size = mod.setting(
    "snake_mouse_segment_size",
    type=int,
    default=20,
    desc="Snake segment width/height."
)

setting_segment_spacing = mod.setting(
    "snake_mouse_segment_spacing",
    type=int,
    default=5,
    desc="Snake segment spacing."
)

setting_maximum_speed = mod.setting(
    "snake_mouse_maximum_speed",
    type=int,
    default=300,
    desc="Snake mouse maximum speed (maximum interval in milliseconds)."
)


ctx = Context()

ctx.matches = r"""
tag: user.snake_mouse_enabled
"""

ctx.lists["self.snake_mouse_toggle"] = ["noodle"]
ctx.lists["self.snake_mouse_pause"] = ["pause"]
ctx.lists["self.snake_mouse_consume"] = ["nom"]
ctx.lists["self.snake_mouse_here"] = ["here"]
ctx.lists["self.snake_mouse_direction"] = ["up", "right", "down", "left"]
ctx.lists["self.snake_mouse_start_position"] = ["center", "here"]
ctx.lists["self.snake_mouse_theme"] = ["dark", "light"]
ctx.lists["self.snake_mouse_speed"] = {
    "super slow": "1",
    "slow": "10",
    "medium": "850",
    "fast": "950"
}


class SnakeMouse:
    def __init__(self):
        self.enabled = False
        self.canvas = None
        self.phrase_metadata = {}
        self.snake = None
    
    def disable(self):
        if not self.enabled:
            return

        speech_system.unregister("phrase", self.update_phrase_metadata)
        actions.mode.disable("user.snake_mouse")
        actions.mode.enable("command")

        self.enabled = False

        if self.canvas:
            self.canvas.close()
            self.canvas = None

        if self.snake:
            self.snake.stop()
            self.snake = None

    def enable(self, start_theme: ActiveTheme, start_position: str, start_direction: Direction, start_speed: int):
        if self.enabled:
            return
        self.enabled = True

        self.screen = ui.screens()[0]
        self.canvas = canvas.Canvas.from_screen(self.screen)

        start_point = self.start_point(start_position)
        dark_theme = SnakeTheme(setting_head_dark_background_color.get(),
                                setting_head_dark_cursor_color.get(),
                                setting_segment_dark_background_color.get())
        light_theme = SnakeTheme(setting_head_light_background_color.get(),
                                setting_head_light_cursor_color.get(),
                                setting_segment_light_background_color.get())
        snake_config = SnakeConfig(dark_theme, light_theme,
                                   setting_maximum_speed.get(),
                                   setting_segment_count.get(),
                                   setting_segment_size.get(),
                                   setting_segment_spacing.get())
        self.snake = Snake(snake_config, start_theme, start_point, start_direction,
                           start_speed)

        self.canvas.register("draw", self.snake.draw)
        self.snake.start()

        ctx.tags = ["user.snake_mouse_active"]

        speech_system.register("phrase", self.update_phrase_metadata)
        actions.mode.enable("user.snake_mouse")
        actions.mode.disable("command")

    def here(self):
        phrase_elapsed = self.phrase_elapsed()
        mouse_point = self.snake.get_here(phrase_elapsed)

        ctrl.mouse_move(mouse_point.x, mouse_point.y)
        snake_mouse_history.add(mouse_point)

    def phrase_elapsed(self):
        if set(["total_ms", "total_ms"]).issubset(set(self.phrase_metadata.keys())):
            return self.phrase_metadata["total_ms"] + self.phrase_metadata["audio_ms"]
        return None

    def start_point(self, start_position: str):
        if start_position == "center":
            return self.canvas.rect.center
        else:
            x, y = ctrl.mouse_pos()
            return Point2d(x, y)

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def update_phrase_metadata(self, j):
        self.phrase_metadata = j["_metadata"]

snake_mouse = SnakeMouse()

@mod.action_class
class Actions:
    def snake_mouse_consume():
        """Set mouse cursor to snake head and deactivate."""
        snake_mouse.here()
        snake_mouse.disable()

    def snake_mouse_change_direction(direction: str):
        """Change snake mouse direction."""
        phrase_elapsed = snake_mouse.phrase_elapsed()
        snake_mouse.snake.change_direction(Direction.from_str(direction), phrase_elapsed)

    def snake_mouse_change_speed(speed: str):
        """Change snake mouse speed."""
        snake_mouse.snake.change_speed(int(speed))

    def snake_mouse_change_theme(theme: str):
        """Change snake mouse theme."""
        snake_mouse.snake.change_theme(ActiveTheme.from_str(theme))

    def snake_mouse_disable():
        """Disable snake mouse"""
        snake_mouse.disable()

    def snake_mouse_enable(start_theme: str, start_position: str, start_direction: str, start_speed: str):
        """Enable snake mouse."""
        snake_mouse.enable(ActiveTheme.from_str(start_theme), start_position, Direction.from_str(start_direction), int(start_speed))

    def snake_mouse_here():
        """Set mouse cursor to snake head."""
        snake_mouse.here()

    def snake_mouse_pause():
        """Pause."""
        snake_mouse.snake.toggle()
