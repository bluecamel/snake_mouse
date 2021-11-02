tag: user.snake_mouse_active
and tag: user.snake_mouse_enabled
and mode: user.snake_mouse
and not mode: sleep
-
{user.snake_mouse_toggle}: user.snake_mouse_disable()

{user.snake_mouse_direction}: user.snake_mouse_change_direction(snake_mouse_direction)

{user.snake_mouse_pause}: user.snake_mouse_pause()

{user.snake_mouse_consume}: user.snake_mouse_consume()
{user.snake_mouse_here}: user.snake_mouse_here()

{user.snake_mouse_theme}: user.snake_mouse_change_theme(snake_mouse_theme)

{user.snake_mouse_speed}: user.snake_mouse_change_speed(snake_mouse_speed)
