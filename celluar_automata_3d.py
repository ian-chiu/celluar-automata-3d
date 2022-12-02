#!/usr/bin/env python3
import glfw
import imgui
import time
from moderngl import CULL_FACE
from rule import Rule
from engine.application import Application
from engine.event import Event
from engine.free_control import FreeControl
from engine.light import DirLight
from engine.model import Model
from engine.orbit_control import OrbitControl
from engine.renderer import Renderer
from engine.material import PhongMaterial
from engine.geometry import BoxGeometry
from engine.event import EventType
from engine.input import is_key_pressed
import engine.gl as gl
from _board import Board


class CelluarAutomata3D(Application):
    def __init__(self):
        super().__init__(window_title="CelluarAutomata3D")
        self.cube = Model(BoxGeometry(),
                          PhongMaterial(color=[0.5, 0.8, 0.1]))
        self.free_control = FreeControl()
        self.orbit_control = OrbitControl(100)
        self.camera_control = self.orbit_control
        self.dir_light = DirLight(direction=[1, -1, 1])
        self.rules = {
            "crystal_growth": Rule("0,1,2,3,4,5,6/1,3/2/VN", 1.0, 0.1),
            "cloud": Rule("13,14,15,16,17,18,19,20,21,22,23,24,25,26"
                          "/13,14,17,18,19/2/M", 0.8, 0.5),
            "slow_decay": Rule("8,11,13,14,15,16,17,18,"
                               "19,20,21,22,23,24,25,26/"
                               "13,14,15,16,17,18,19,20,21,22,23,24,25,26/5/M",
                               0.5, 1.0),
            "445": Rule("4/4/5/M", 0.1, 1.0)
        }
        self.board = Board(50, self.rules['crystal_growth'], 0.4)
        self.paused = True
        self.evolve_period = 0.1
        self.last_board_update_time = time.time()
        self._rule_current_index = 0
        gl.ctx.disable(CULL_FACE)

    def on_update(self, delta_time: float):
        if is_key_pressed(glfw.KEY_ESCAPE):
            self.running = False
        self.camera_control.on_update(delta_time)

        curr_time = time.time()
        dt = curr_time - self.last_board_update_time
        if not self.paused and dt > self.evolve_period:
            self.board.update()
            self.last_board_update_time = time.time()

    def on_event(self, event: Event):
        self.camera_control.on_event(event)
        if event.type == EventType.KeyPressedEvent:
            if event.key == glfw.KEY_SPACE and not event.repeated:
                self.paused = not self.paused
            if self.paused and event.key == glfw.KEY_RIGHT \
                    and not event.repeated:
                self.board.update()

    def on_render(self):
        Renderer.begin_scene(
            camera=self.camera_control.camera,
            dir_light=self.dir_light
        )
        Renderer.draw_batch(self.board.vertex_buffer)
        Renderer.end_scene()

    def on_render_gui(self):
        self._draw_control_panel_gui()

    def _draw_control_panel_gui(self):
        def draw_rules_gui():
            expanded, _ = imgui.collapsing_header("Rules")
            if expanded:
                keys = [str(k) for k in self.rules]
                clicked, self._rule_current_index = imgui.listbox(
                    "##listbox_rules", self._rule_current_index, keys
                )
                if clicked:
                    self.board.set_rule(
                        self.rules[keys[self._rule_current_index]])

        def draw_debug_info_gui():
            expanded, _ = imgui.collapsing_header("Debug")
            if expanded:
                imgui.text(f"FPS: {self.fps:.1f}")
                imgui.text(f"Quads: {self.board.get_quad_count():.1f}")

        imgui.begin("Control Panel")
        draw_rules_gui()
        draw_debug_info_gui()
        imgui.end()



if __name__ == "__main__":
    app = CelluarAutomata3D()
    app.run()
