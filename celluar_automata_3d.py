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
        self.rule_current_index = 0
        self.randomise_radius = self.board.get_rule().initial_radius
        self.randomise_density = self.board.get_rule().initial_density
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
            if not event.repeated:
                if event.key == glfw.KEY_SPACE:
                    self.paused = not self.paused
                if self.paused and event.key == glfw.KEY_F:
                    self.board.update()
                if event.key == glfw.KEY_R:
                    self.board.randomise(self.randomise_radius,
                                         self.randomise_density)
                if event.key == glfw.KEY_E:
                    self.board.clear()
                if event.key == glfw.KEY_C:
                    self.camera_control = self.orbit_control \
                        if self.camera_control == self.free_control \
                        else self.free_control
                if event.key == glfw.KEY_Q or event.key == glfw.KEY_ESCAPE:
                    self.running = False

    def on_ready(self):
        imgui.new_frame()
        imgui.set_next_window_size(450, 700)
        imgui.set_next_window_position(10, 10)
        self._draw_control_panel_gui()
        imgui.render()

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
        flags = imgui.TREE_NODE_DEFAULT_OPEN

        def draw_help():
            expanded, _ = imgui.collapsing_header("Help")
            if expanded:
                imgui.text("GENERAL")
                imgui.bullet_text("R: randomise by factors in settings")
                imgui.bullet_text("E: erase all cells")
                imgui.bullet_text("Spacebar: pause/continue simulation")
                imgui.bullet_text("F: update one step forward")
                imgui.bullet_text("Q/Esc: quit the application")
                imgui.bullet_text("Different rules can be selected "
                                  "in Rules section")

                imgui.text("CAMERA")
                imgui.bullet_text("There are two camera controllers: "
                                  "Free and Orbit Controller")
                imgui.bullet_text("C: toggle between two controllers")

                imgui.bullet_text("While in free mode:")
                imgui.indent()
                imgui.bullet_text("Pressed mouse right and move to "
                                  "rotate the camera")
                imgui.bullet_text("WASD: move the camera")
                imgui.bullet_text("Scroll mouse wheel to change "
                                  "the moving speed")
                imgui.unindent()

                imgui.bullet_text("While in orbit mode:")
                imgui.indent()
                imgui.bullet_text("Pressed mouse right and move to "
                                  "rotate the camera")
                imgui.bullet_text("Scroll mouse wheel to zoom in/out")
                imgui.unindent()
                imgui.separator()

        def draw_status():
            expanded, _ = imgui.collapsing_header("Status", flags=flags)
            if expanded:
                imgui.text(f"FPS: {self.fps:.1f}")
                imgui.text(f"Quad Count: {self.board.get_quad_count()}")
                imgui.text(f"Paused: {self.paused}")

        def draw_rules():
            expanded, _ = imgui.collapsing_header("Rules", flags=flags)
            if expanded:
                keys = [str(k) for k in self.rules]
                clicked, self.rule_current_index = imgui.listbox(
                    "##listbox_rules", self.rule_current_index, keys
                )
                if clicked:
                    selected_rule = self.rules[keys[self.rule_current_index]]
                    self.board.set_rule(selected_rule)
                    self.randomise_radius = selected_rule.initial_radius
                    self.randomise_density = selected_rule.initial_density

        def draw_settings():
            expanded, _ = imgui.collapsing_header("Settings", flags=flags)
            if expanded:
                changed = False
                changed, value = imgui.drag_float(
                    "evolve seconds",
                    value=self.evolve_period,
                    change_speed=0.01,
                    min_value=0.01,
                    max_value=5.0,
                    format='%.2f'
                )
                if changed:
                    self.evolve_period = value

                changed = False
                changed, value = imgui.drag_int(
                    "border side",
                    value=self.board.get_side(),
                    change_speed=1,
                    min_value=10,
                    max_value=70,
                    format='%.2f'
                )
                if changed:
                    self.board.set_side(value)

                changed = False
                changed, value = imgui.drag_float(
                    "randomise radius",
                    value=self.randomise_radius,
                    change_speed=0.01,
                    min_value=0.05,
                    max_value=1.0,
                    format='%.2f'
                )
                if changed:
                    self.randomise_radius = value

                changed = False
                changed, value = imgui.drag_float(
                    "randomise density",
                    value=self.randomise_density,
                    change_speed=0.01,
                    min_value=0.05,
                    max_value=1.0,
                    format='%.2f'
                )
                if changed:
                    self.randomise_density = value

        imgui.begin("Control Panel")
        draw_help()
        draw_status()
        draw_settings()
        draw_rules()
        imgui.end()


if __name__ == "__main__":
    app = CelluarAutomata3D()
    app.run()
