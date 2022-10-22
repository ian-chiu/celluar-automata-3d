from typing import Optional
from moderngl import VertexArray
import glm
from engine.camera import Camera

class Renderer:
    camera: Optional[Camera] = None

    @staticmethod
    def begin_scene(camera):
        self = Renderer
        self.camera = camera

    @staticmethod
    def end_scene():
        pass

    @staticmethod
    def submit(vao: VertexArray,
               transform: glm.mat4 = glm.mat4(1.0)) -> None:
        self = Renderer
        if self.camera:
            vao.program['u_ViewProjection'].write(self.camera.view_proj_matrix)
        vao.program['u_Transform'].write(transform)
        vao.render()
