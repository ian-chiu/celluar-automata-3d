from moderngl import Context, VertexArray
from typing import Dict
from engine.vbo import *
from engine.utils import *


class ShaderManager:
    shaders = {}

    @staticmethod
    def begin(ctx: Context):
        self = ShaderManager
        self.shaders['orange'] = load_shader(ctx, 'orange')
        self.shaders['flat'] = load_shader(ctx, 'flat')

    @staticmethod
    def end():
        self = ShaderManager
        [program.release() for program in self.shaders.values()]


class VboManager:
    vbos: Dict[str, BaseVbo] = {}

    @staticmethod
    def begin(ctx: Context):
        self = VboManager
        self.vbos['triangle'] = TriangleVbo(ctx)
        self.vbos['cube'] = CubeVbo(ctx)

    @staticmethod
    def end():
        self = VboManager
        [vbo.destroy() for vbo in self.vbos.values()]
