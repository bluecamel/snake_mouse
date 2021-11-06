tag: user.snake_mouse_history_active
and tag: user.snake_mouse_history_enabled
and mode: user.snake_mouse_history
and not mode: sleep
-
close: user.snake_mouse_history_disable()
<number_small>: user.snake_mouse_history_select(number_small)
