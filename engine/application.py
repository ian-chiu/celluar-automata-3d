from typing import Optional
import pygame as pg
import moderngl as mgl
import sys
from engine.renderer import Renderer
from engine.shader import Shader
from engine.orbit_control import OrbitControl
import engine.gl as gl


class Application:
    def __init__(self, window_size=(1600, 900), window_title="Application"):
        self._window_size = window_size
        # init pygame module
        pg.init()
        # set opengl attributes
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        self._surface = pg.display.set_mode(self._window_size,
            pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
        pg.display.set_caption(window_title)
        # mouse settings
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        # create an object to help track time
        self.clock = pg.time.Clock()
        # prepare singletons
        gl.GLUtils.set_context()
        gl.ctx.enable(flags=mgl.DEPTH_TEST)
        Shader.init()
        Renderer.init()

    def on_update(self, delta_time: float):
        pass

    def on_event(self, event: pg.event.Event):
        pass

    def on_render(self):
        pass

    def run(self):
        last_frame_time = pg.time.get_ticks()
        while True:
            current_frame_time = pg.time.get_ticks()
            delta_time = (current_frame_time - last_frame_time) / 1000
            self._check_events()
            if delta_time != 0.0:
                self._update(delta_time)
            self._render()
            self.clock.tick(60)

    def _shutdown(self):
        Shader.shutdown()
        pg.quit()
        sys.exit()

    def _check_events(self):
        for event in pg.event.get():
            if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                    or event.type == pg.QUIT:
                self._shutdown()
            if event.type == pg.VIDEORESIZE:
                self._window_size = (event.w, event.h)
                self._create_surface()
            self.on_event(event)

    def _update(self, delta_time: float):
        self.on_update(delta_time)

    def _render(self):
        if not gl:
            return
        gl.ctx.clear(0.1, 0.1, 0.1)
        self.on_render()
        pg.display.flip()

    def _create_surface(self):
        self._surface = pg.display.set_mode(self._window_size,
            pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

if __name__ == "__main__":
    app = Application()
    app.run()
