from typing import Optional
from moderngl import  Context, Program, VertexArray
import glm
from engine.geometry import BaseGeometry
from engine.material import BaseMaterial
import engine.gl as gl

class Model:
    def __init__(
            self,
            geometry: BaseGeometry,
            material: BaseMaterial,
            transform = glm.mat4(1.0)
            ) -> None:
        self.transform = transform
        self.material = material
        self.shader = material.shader
        self.vertex_array = gl.ctx.vertex_array(self.shader,
               [(geometry.buffer, geometry.format, *geometry.attributes)],
               skip_errors=True)
