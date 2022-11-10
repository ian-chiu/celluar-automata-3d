import pygame as pg
import glm
from engine.camera import Camera


class FreeControl:
    def __init__(self, radius = 10):
        self.camera = Camera()
        self.camera.position = glm.vec3(0, 0, radius)
        self._radius = radius
        self._speed = 0.03
        self._is_first_mouse = True
        self._last_x = 0
        self._last_y = 0

    def on_event(self, event: pg.event.Event):
        if event.type == pg.VIDEORESIZE:
            w, h = pg.display.get_surface().get_size()
            self.camera.aspect = w / h
        if event.type == pg.MOUSEWHEEL:
            sensitivity = 0.001
            y = event.y * sensitivity
            self.camera.fov -= y

    def on_update(self, delta_time: float):
        right = glm.normalize(glm.cross(self.camera.front, self.camera.up))
        updated_position = glm.vec3(self.camera.position)
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_w]:
            updated_position += self.camera.front * delta_time * self._speed
        elif key_pressed[pg.K_s]:
            updated_position -= self.camera.front * delta_time * self._speed
        if key_pressed[pg.K_a]:
            updated_position -= right * delta_time * self._speed
        elif key_pressed[pg.K_d]:
            updated_position += right * delta_time * self._speed
        self.camera.position = updated_position

        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[pg.BUTTON_LEFT]:
            if self._is_first_mouse:
                self._last_x, self._last_y = pg.mouse.get_pos()
                self._is_first_mouse = False
                pg.mouse.set_visible(False)
            x, y = pg.mouse.get_pos()
            x_offset = x - self._last_x
            y_offset = self._last_y - y
            self._last_x = x
            self._last_y = y
            sensitivity = 0.3
            self.camera.yaw += x_offset * sensitivity
            self.camera.pitch += y_offset * sensitivity
        else:
            if not self._is_first_mouse:
                pg.mouse.set_visible(True)
            self._is_first_mouse = True
