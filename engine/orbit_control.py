import glm
import glfw
from engine.application import Application
from engine.camera import Camera
from engine.event import Event, EventType
from engine.input import get_mouse_position, is_key_pressed, is_mouse_pressed, \
                         set_cursor_visable

class OrbitControl:
    def __init__(self, radius = 10):
        self.camera = Camera()
        self.camera.position = glm.vec3(0, 0, radius)
        self._radius = radius
        self._speed = 5.0
        self._orbit_yaw = 0
        self._orbit_pitch = 0
        self._focus_point = glm.vec3(0, 0, 0)
        self._is_first_mouse = True
        self._last_x = 0
        self._last_y = 0

    def on_event(self, event: Event):
        if event.type == EventType.WindowResized:
            w = Application.window.width
            h = Application.window.height
            self.camera.aspect = w / h
        if event.type == EventType.MouseScrolled:
            self._zoom(event.y)

    def on_update(self, delta_time: float):
        if is_key_pressed(glfw.KEY_KP_ADD):
            self._zoom(self._speed * delta_time)
        if is_key_pressed(glfw.KEY_KP_SUBTRACT):
            self._zoom(-self._speed * delta_time)
        if is_mouse_pressed(glfw.MOUSE_BUTTON_1):
            if self._is_first_mouse:
                self._last_x, self._last_y = get_mouse_position()
                self._is_first_mouse = False
                set_cursor_visable(False)
            x, y = get_mouse_position()
            x_offset = self._last_x - x
            y_offset = self._last_y - y
            self._last_x = x
            self._last_y = y
            sensitivity = 0.5
            self._orbit_yaw += x_offset * sensitivity
            self._orbit_pitch += y_offset * sensitivity
            self._orbit_pitch = min(self._orbit_pitch, 89.0)
            self._orbit_pitch = max(self._orbit_pitch, -89.0)
            updated_position = glm.vec3()
            updated_position.x = glm.sin(glm.radians(self._orbit_yaw)) \
                * glm.cos(glm.radians(self._orbit_pitch)) * self._radius
            updated_position.y = glm.sin(glm.radians(
                self._orbit_pitch)) * self._radius
            updated_position.z = glm.cos(glm.radians(self._orbit_yaw)) \
                * glm.cos(glm.radians(self._orbit_pitch)) * self._radius
            self.camera.position = updated_position
            self.camera.focus(self._focus_point)
        else:
            if not self._is_first_mouse:
                set_cursor_visable(True)
            self._is_first_mouse = True

    def _zoom(self, y_offset):
        sensitivity = 0.05
        y_offset *= sensitivity
        self.camera.fov -= y_offset
