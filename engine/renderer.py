from typing import Optional, List, TypedDict, overload, Tuple
import glm
import numpy as np
from moderngl import LINE_STRIP, LINES, Program, VertexArray, TextureCube, Buffer
from engine.camera import Camera
from engine.geometry import EnvBoxGemoetry
from engine.model import Model
from engine.shader import Shader
from engine.light import DirLight, PointLight
import engine.gl as gl
from engine.texture import get_white_texture

N_MAX_POINT_LIGHTS = 8
MAX_BUFFER_SIZE = 3600000


class Renderer:
    camera: Optional[Camera] = None
    skybox: Optional[VertexArray] = None
    env_map: Optional[TextureCube] = None
    point_lights: List[PointLight] = []
    dir_light: Optional[DirLight] = None
    shader: Optional[Program] = None
    batch_layout = {
        "format": "3f 2f 3f 4f",
        "attributes": ["a_Position", "a_UV", "a_Normal", "a_Color"]
    }

    # for batch rendering
    _vertex_buffer: Optional[Buffer] = None
    _quad_index_buffer: Optional[Buffer] = None
    _vertex_array: Optional[VertexArray] = None

    @staticmethod
    def init():
        self = Renderer
        geo = EnvBoxGemoetry()
        self.skybox = gl.ctx.vertex_array(
            Shader.background, [(geo.buffer, geo.format, *geo.attributes)],
            skip_errors=True)

        self.shader = Shader.flat
        quad_indices = []
        offset = 0
        for i in range(0, MAX_BUFFER_SIZE, 6):
            quad_indices.append(offset + 0)
            quad_indices.append(offset + 1)
            quad_indices.append(offset + 2)
            quad_indices.append(offset + 2)
            quad_indices.append(offset + 3)
            quad_indices.append(offset + 0)
            offset += 4
        quad_indices = np.array(quad_indices, dtype="int32")
        self._quad_index_buffer = gl.ctx.buffer(quad_indices)
        self._vertex_buffer = gl.ctx.buffer(np.zeros(
            MAX_BUFFER_SIZE, dtype="float32"), dynamic=True)
        self._vertex_array = gl.ctx.vertex_array(
            self.shader,
            [(self._vertex_buffer, self.batch_layout["format"],
              *self.batch_layout["attributes"])],
            index_buffer=self._quad_index_buffer,
            skip_errors=True)

    @staticmethod
    def begin_scene(camera: Camera,
                    point_lights: List[PointLight] = [],
                    dir_light: Optional[DirLight] = None,
                    env_map: Optional[TextureCube] = None,
                    ) -> None:
        self = Renderer
        self.camera = camera
        self.env_map = env_map
        self.point_lights = point_lights
        self.dir_light = dir_light

    @staticmethod
    def end_scene():
        self = Renderer
        self._draw_background()

    @staticmethod
    def submit(vao: VertexArray,
               transform: glm.mat4 = glm.mat4(1.0)) -> None:
        self = Renderer
        if self.camera:
            vao.program['u_ViewProjection'].write(self.camera.view_proj_matrix)
        vao.program['u_Transform'].write(transform)
        vao.render()

    @staticmethod
    def draw_batch(vertices):
        self = Renderer
        get_white_texture().use()
        vao = self._vertex_array
        if self.camera:
            vao.program['u_ViewProjection'].write(self.camera.view_proj_matrix)
        vao.program['u_Transform'].write(glm.identity(glm.mat4))
        if self.dir_light:
            self.upload_dir_light(vao.program)
        self._vertex_buffer.write(vertices)
        vao.render()

    @staticmethod
    def clear_vertex_buffer():
        self = Renderer
        self._vertex_buffer.clear()

    @staticmethod
    def draw_model(model: Model, position: Tuple[float, float, float]) -> None:
        self = Renderer
        model.material.use()
        if not model.shader:
            return
        if self.camera:
            model.shader['u_ViewProjection'].write(
                self.camera.view_proj_matrix)
            model.shader['u_ViewPosition'].write(
                self.camera.position)
        transform = glm.translate(position)
        model.shader['u_Transform'].write(transform * model.transform)
        self.upload_point_lights(model.shader)
        if self.dir_light:
            self.upload_dir_light(model.shader)
        model.vertex_array.render()

    @staticmethod
    def _draw_background():
        self = Renderer
        if not self.env_map or not self.skybox:
            return
        self.skybox.program['u_Cubemap'] = 0
        self.env_map.use(location=0)
        if self.camera:
            view_matrix = glm.mat4(glm.mat3(self.camera.view_matrix))
            view_proj_matrix = self.camera.proj_matrix * view_matrix
            self.skybox.program['u_ViewProjection'].write(view_proj_matrix)
        gl.ctx.depth_func = '<='
        self.skybox.render()
        gl.ctx.depth_func = '<'

    @staticmethod
    def upload_point_lights(program: Program) -> None:
        if program.get("u_PointLights", None):
            return
        self = Renderer
        if self.point_lights and len(self.point_lights):
            program['u_NPointLights'].write(
                glm.int32(len(self.point_lights)))
        for i in range(min(N_MAX_POINT_LIGHTS, len(self.point_lights))):
            point_light = self.point_lights[i]
            name = f'u_PointLights[{i}]'
            program[name + '.linear'].write(point_light.linear)
            program[name + '.quadratic'].write(point_light.quadratic)
            program[name + '.position'].write(point_light.position)
            program[name + '.ambient'].write(point_light.ambient)
            program[name + '.diffuse'].write(point_light.diffuse)
            program[name + '.specular'].write(point_light.specular)

    @staticmethod
    def upload_dir_light(program: Program) -> None:
        if program.get("u_DirLight", None):
            return
        self = Renderer
        program['u_DirLight.direction'].write(self.dir_light.direction)
        program['u_DirLight.ambient'].write(self.dir_light.ambient)
        program['u_DirLight.diffuse'].write(self.dir_light.diffuse)
        program['u_DirLight.specular'].write(self.dir_light.specular)
