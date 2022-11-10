#!/usr/bin/env python3
import pygame as pg
from pathlib import Path
from engine.application import Application
from engine.light import DirLight, PointLight
from engine.model import Model
from engine.orbit_control import OrbitControl
from engine.free_control import FreeControl
from engine.renderer import Renderer
from engine.material import PhongMaterial, FlatMaterial
from engine.geometry import BoxGeometry
from engine.texture import load_texture_cube

class CelluarAutomata3D(Application):
    def __init__(self):
        super().__init__(window_title="CelluarAutomata3D")
        self.cube = Model(BoxGeometry(),
            PhongMaterial(Path("assets/textures/images/uvtest.png")))
        self.camera_control = OrbitControl()
        self.point_lights = [
            PointLight(position=[-10, -10, -10]),
            PointLight(position=[ 10, -10, -10]),
            PointLight(position=[ 10, -10,  10]),
            PointLight(position=[-10, -10,  10]),
            PointLight(position=[-10,  10, -10]),
            PointLight(position=[ 10,  10, -10]),
            PointLight(position=[ 10,  10,  10]),
            PointLight(position=[-10,  10,  10]),
        ]
        self.env_map = load_texture_cube(
            Path('assets/textures/cubemaps/lake'), 'jpg')

    def on_update(self, delta_time: float):
        self.camera_control.on_update(delta_time)

    def on_event(self, event: pg.event.Event):
        self.camera_control.on_event(event)

    def on_render(self):
        Renderer.begin_scene(
            camera=self.camera_control.camera,
            point_lights=self.point_lights,
            env_map=self.env_map
        )
        Renderer.draw_model(self.cube)
        Renderer.end_scene()

if __name__ == "__main__":
    app = CelluarAutomata3D()
    app.run()
