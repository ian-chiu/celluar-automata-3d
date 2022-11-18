import glm
from imgui.integrations.glfw import glfw
from engine.application import Application
from engine.camera import Camera
from engine.event import Event, EventType
from engine.input import get_mouse_position, is_key_pressed, \
                         is_mouse_pressed, set_cursor_visable


class FreeControl:
    def __init__(self):
        self.camera = Camera()
        self.camera.position = glm.vec3(0, 0, 0)
        self._speed = 1
        self._is_first_mouse = True
        self._last_x = 0
        self._last_y = 0

    def on_event(self, event: Event):
        if event.type == EventType.WindowResized:
            w = Application.window.width
            h = Application.window.height
            self.camera.aspect = w / h
        if event.type == EventType.MouseScrolled:
            sensitivity = 0.001
            y = event.y * sensitivity
            self.camera.fov -= y

    def on_update(self, delta_time: float):
        right = glm.normalize(glm.cross(self.camera.front, self.camera.up))
        updated_position = glm.vec3(self.camera.position)
        if is_key_pressed(glfw.KEY_W):
            updated_position += self.camera.front * delta_time * self._speed
        elif is_key_pressed(glfw.KEY_S):
            updated_position -= self.camera.front * delta_time * self._speed
        if is_key_pressed(glfw.KEY_A):
            updated_position -= right * delta_time * self._speed
        elif is_key_pressed(glfw.KEY_D):
            updated_position += right * delta_time * self._speed
        self.camera.position = updated_position

        if is_mouse_pressed(glfw.MOUSE_BUTTON_1):
            if self._is_first_mouse:
                self._last_x, self._last_y = get_mouse_position()
                self._is_first_mouse = False
                set_cursor_visable(False)
            x, y = get_mouse_position()
            x_offset = x - self._last_x
            y_offset = self._last_y - y
            self._last_x = x
            self._last_y = y
            sensitivity = 0.3
            self.camera.yaw += x_offset * sensitivity
            self.camera.pitch += y_offset * sensitivity
        else:
            if not self._is_first_mouse:
                set_cursor_visable(True)
            self._is_first_mouse = True
