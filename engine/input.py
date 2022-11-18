from typing import Tuple
import glfw
from engine.application import Application

def is_key_pressed(key: int) -> bool:
    assert Application.window
    window = Application.window.window
    state = glfw.get_key(window, key)
    return state == glfw.PRESS or state == glfw.REPEAT

def is_mouse_pressed(button: int) -> bool:
    assert Application.window
    window = Application.window.window
    state = glfw.get_mouse_button(window, button)
    return state == glfw.PRESS or state == glfw.REPEAT

def get_mouse_position() -> Tuple[float, float]:
    assert Application.window
    window = Application.window.window
    return glfw.get_cursor_pos(window)

def get_mouse_x() -> float:
    return get_mouse_position()[0]

def get_mouse_y() -> float:
    return get_mouse_position()[1]

def set_cursor_visable(enabled: bool) -> None:
    assert Application.window
    window = Application.window.window
    if enabled:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    else:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
