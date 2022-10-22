#!/usr/bin/env python3
import pygame as pg
from engine.application import Application
from engine.resource_manager import *
from engine.orbit_control import OrbitControl
from engine.renderer import Renderer

class CelluarAutomata3D(Application):
    def __init__(self):
        super().__init__()
        shaders = ShaderManager.shaders
        vbos = VboManager.vbos
        self.cube = get_vao(self.ctx, shaders['orange'], vbos['cube'])
        self.orbit_control = OrbitControl()

    def on_update(self, delta_time: float):
        self.orbit_control.on_update(delta_time)

    def on_event(self, event: pg.event.Event):
        self.orbit_control.on_event(event)

    def on_render(self):
        Renderer.begin_scene(self.orbit_control.camera)
        Renderer.submit(self.cube)
        Renderer.end_scene()

if __name__ == "__main__":
    app = CelluarAutomata3D()
    app.run()
