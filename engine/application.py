from typing import Optional
import moderngl as mgl
import glfw
from engine.event import Event
from engine.renderer import Renderer
from engine.shader import Shader
from engine.window import Window
import engine.gl as gl
import imgui.core as imgui
from imgui.integrations.glfw import GlfwRenderer


class Application:
    window = None

    def __init__(self, window_size=(1600, 900), window_title="Application"):
        if Application.window == None:
           Application.window = Window(window_size[0], window_size[1],
                                       window_title)
        window = Application.window
        window.event_callback = self._check_events
        self.running = True
        self.fps = 0.0
        gl.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        Shader.init()
        Renderer.init()

    def on_update(self, delta_time: float):
        pass

    def on_event(self, event):
        pass

    def on_render(self):
        pass

    def on_render_gui(self):
        pass

    def run(self):
        prev_time = glfw.get_time()
        frame_count = 0
        while self.running:
            frame_count += 1
            curr_time = glfw.get_time()
            delta_time = curr_time - prev_time
            if delta_time > 0.5:
                self.fps = frame_count / delta_time
                prev_time = curr_time
                frame_count = 0
            self._update(delta_time)
            self._render()

    def _shutdown(self):
        Shader.shutdown()

    def _check_events(self, event: Event):
        self.on_event(event)

    def _update(self, delta_time: float):
        Application.window.on_update()
        self.on_update(delta_time)

    def _render_gui(self):
        imgui.new_frame()
        self.on_render_gui()
        imgui.render()
        Application.window.render_gui(imgui.get_draw_data())

    def _render(self):
        gl.ctx.clear(0.1, 0.1, 0.1)
        self.on_render()
        self._render_gui()


if __name__ == "__main__":
    app = Application()
    app.run()
