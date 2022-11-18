#!/usr/bin/env python3
import glm
import glfw
import imgui
import numpy as np
from engine.application import Application
from engine.event import Event
from engine.input import is_key_pressed
from engine.light import DirLight
from engine.model import Model
from engine.orbit_control import OrbitControl
from engine.renderer import Renderer
from engine.material import PhongMaterial
from engine.geometry import BoxGeometry
from engine.event import EventType
from _board import Board
from rule import Rule


class CelluarAutomata3D(Application):
    def __init__(self):
        super().__init__(window_title="CelluarAutomata3D")
        self.cube = Model(BoxGeometry(),
            PhongMaterial(color=[0.5, 0.8, 0.1]))
        self.camera_control = OrbitControl(100)
        self.dir_light = DirLight(direction=[1, -1, 1])
        self.rule = Rule("0,1,2,3,4,5,6/1,3/2/VN", 1.0, 0.05)
        self.board = Board(20, self.rule)
        self.paused = True
        self.draw_call_count = 0

    def on_update(self, delta_time: float):
        if is_key_pressed(glfw.KEY_ESCAPE):
            self.running = False
        self.camera_control.on_update(delta_time)
        if not self.paused:
            self.board.update(delta_time)

    def on_event(self, event: Event):
        self.camera_control.on_event(event)
        if event.type == EventType.KeyPressedEvent:
            if event.key == glfw.KEY_SPACE and not event.repeated:
                self.paused = not self.paused

    def on_render_gui(self):
        imgui.begin("Debug", True)
        imgui.text(f"FPS: {self.fps:.1f}")
        imgui.text(f"Draw Calls: {self.draw_call_count}")
        imgui.end()

    def on_render(self):
        Renderer.begin_scene(
            camera=self.camera_control.camera,
            dir_light=self.dir_light
        )
        self._render_board()
        Renderer.end_scene()

    def _render_board(self):
        self.draw_call_count = 0
        for index, cell in enumerate(self.board.cells):
            if cell == 0:
                continue
            pos = glm.vec3(list(self.board.get_coordinate(index)))
            pos -= self.board.side / 2
            transform = glm.translate(pos)
            Renderer.draw_model(self.cube, transform)
            self.draw_call_count += 1


if __name__ == "__main__":
    app = CelluarAutomata3D()
    app.run()
