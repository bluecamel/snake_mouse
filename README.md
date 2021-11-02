# Talon Snake Mouse

This is a silly experiment that turned into something pretty useful.  The original idea was to turn the mouse cursor into the classic snake game.  The end result is basically that, with some changes that are more suited for a voice controlled mouse alternative (e.g. no collisions and absolute instead of relative turns).

# Basic Usage
To start the snake mouse, simply say `noodle`.  A snake will show up with its head at the current mouse cursor position, moving to the right.  Saying `noodle` again will disable the snake mouse.

## Commands While Active
While the snake mouse is active, commands are available to pause, change direction, change speed, change theme, and move the mouse cursor to the current position of the snake head.  Many of these can also be set in the initial command to activate the snake mouse.

### Pause
The snake mouse can be paused by saying `pause`.  Saying `pause` again will resume the previous motion.

### Here
The mouse cursor can be moved to the current position of the snake head by saying `here`.

### Consume
Saying `nom` will move the mouse cursor to the current position of the snake head and disable the snake mouse.

### Direction
Change direction by saying the desired direction (e.g. `up`, `right`, `down`, `down`).

### Speed
Change speed by saying the desired speed (e.g. `slow`, `medium`, `fast`).

### Theme
Change theme by saying the desired theme (e.g. `dark`, `light`).

# Advanced Usage
There are few options for how the snake mouse starts that can be controlled by the initial activate command.  The format for the toggle command is:
```
{toggle} [{theme}] [{start_position}] [{direction}] [{speed}]
```

## Start Position
The start position is either `center` (the center of the screen) or `here` (the  current mouse cursor position, which is the default).

## Example

Light theme, moving slowly left from the current mouse position:
```
noodle light left slow
```

# Customization
All commands/captures are defined in context lists, so can be easily overridden.  Themes and segment count, size, and spacing are defined as settings (see `snake_mouse_settings.talon`).
