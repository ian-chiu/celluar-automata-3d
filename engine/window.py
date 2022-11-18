from typing import Callable, TypedDict
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
import engine.gl as gl
from engine.event import Event, KeyPressedEvent, MouseScrolledEvent, \
                         WindowResizedEvent

def _glfw_error_callback(error: int, description: str):
    print(f"GLFW Error {error}: {description}")

class WindowData(TypedDict):
    width: int
    height: int
    title: str
    event_callback: Callable[[Event], None]

class Window:
    def __init__(self, width = 1200, height = 720, title = "Title"):
        self._data: WindowData = {
            'width': width,
            'height': height,
            'title': title,
            'event_callback': lambda event: None
        }
        success = glfw.init()
        assert success, "Could not initialize glfw."
        self.window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(self.window)
        gl.GLUtils.set_context()

        glfw.set_error_callback(_glfw_error_callback)
        glfw.set_window_user_pointer(self.window, self._data)
        glfw.set_framebuffer_size_callback(self.window, self._resize_callback)
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_char_callback(self.window, self._char_callback)

        imgui.create_context()
        self.impl = GlfwRenderer(self.window, False)

    def render_gui(self, data):
        self.impl.render(data)

    def on_update(self):
        glfw.swap_buffers(self.window)
        glfw.poll_events()
        self.impl.process_inputs()

    def _resize_callback(self, window: glfw._GLFWwindow, width: int,
                         height: int):
        self.impl.resize_callback(window, width, height)
        gl.ctx.viewport = (0, 0, width, height)
        data = glfw.get_window_user_pointer(window)
        data['width'] = width
        data['height'] = height
        data['event_callback'](WindowResizedEvent(width, height))

    def _key_callback(self, window: glfw._GLFWwindow, key: int, scancode: int,
                      action: int, mods: int):
        self.impl.keyboard_callback(window, key, scancode, action, mods)
        data = glfw.get_window_user_pointer(window)
        event = KeyPressedEvent(key, int(action == glfw.PRESS))
        data['event_callback'](event)

    def _scroll_callback(self, window, x, y):
        self.impl.scroll_callback(window, x, y)
        data = glfw.get_window_user_pointer(window)
        data['event_callback'](MouseScrolledEvent(x, y))

    def _char_callback(self, window, char):
        self.impl.char_callback(window, char)

    @property
    def event_callback(self):
        return self._data['event_callback']

    @event_callback.setter
    def event_callback(self, fn: Callable[[Event], None]):
        self._data['event_callback'] = fn

    @property
    def width(self):
        return self._data['width']

    @property
    def height(self):
        return self._data['height']
