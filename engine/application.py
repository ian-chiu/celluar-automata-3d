from typing import Optional
import pygame as pg
import moderngl as mgl
import sys
from engine.renderer import Renderer
from engine.resource_manager import ShaderManager, VboManager
from engine.utils import get_vao
from engine.orbit_control import OrbitControl

class Application:
    def __init__(self, window_size=(1600, 900)):
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
        # mouse settings
        pg.event.set_grab(True)
        pg.mouse.set_visible(True)
        # detect and use existing opengl context
        self.ctx = mgl.create_context()
        # create an object to help track time
        self.clock = pg.time.Clock()
        # prepare reource managers
        ShaderManager.begin(self.ctx)
        VboManager.begin(self.ctx)

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

    def _check_events(self):
        for event in pg.event.get():
            if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                    or event.type == pg.QUIT:
                VboManager.end()
                ShaderManager.end()
                pg.quit()
                sys.exit()
            if event.type == pg.VIDEORESIZE:
                self._window_size = (event.w, event.h)
                self._create_surface()
            self.on_event(event)

    def _update(self, delta_time: float):
        self.on_update(delta_time)

    def _render(self):
        self.ctx.clear(0.1, 0.1, 0.1)
        self.on_render()
        pg.display.flip()

    def _create_surface(self):
        self._surface = pg.display.set_mode(self._window_size,
            pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

if __name__ == "__main__":
    app = Application()
    app.run()
