import pygame as pg
import glm
from engine.utils import is_mouse_pressed
from engine.camera import Camera

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

    def on_event(self, event: pg.event.Event):
        if event.type == pg.VIDEORESIZE:
            w, h = pg.display.get_surface().get_size()
            self.camera.aspect = w / h
        if event.type == pg.MOUSEWHEEL:
            sensitivity = 0.05
            y = event.y * sensitivity
            self.camera.fov -= y

    def on_update(self, delta_time: float):
        if is_mouse_pressed(pg.BUTTON_LEFT):
            if self._is_first_mouse:
                self._last_x, self._last_y = pg.mouse.get_pos()
                self._is_first_mouse = False
                pg.mouse.set_visible(False)
            x, y = pg.mouse.get_pos()
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
                pg.mouse.set_visible(True)
            self._is_first_mouse = True
