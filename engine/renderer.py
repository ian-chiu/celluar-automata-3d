from typing import Optional, List
from moderngl import VertexArray, TextureCube
import glm
from engine.camera import Camera
from engine.geometry import EnvBoxGemoetry
from engine.model import Model
from engine.shader import Shader
from engine.light import DirLight, PointLight
import engine.gl as gl

N_MAX_POINT_LIGHTS = 8

class Renderer:
    camera: Optional[Camera] = None
    skybox: Optional[VertexArray] = None
    env_map: Optional[TextureCube] = None
    point_lights: List[PointLight] = []
    dir_light: Optional[DirLight] = None

    @staticmethod
    def init():
        self = Renderer
        geo = EnvBoxGemoetry()
        self.skybox = gl.ctx.vertex_array(Shader.background,
            [(geo.buffer, geo.format, *geo.attributes)], skip_errors=True)

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
    def draw_model(model: Model, transform = glm.identity(glm.mat4)) -> None:
        self = Renderer
        model.material.use()
        if not model.shader:
            return
        if self.camera:
            model.shader['u_ViewProjection'].write(
                self.camera.view_proj_matrix)
            model.shader['u_ViewPosition'].write(
                self.camera.position)
        model.shader['u_Transform'].write(transform * model.transform)
        self._upload_point_lights(model)
        if self.dir_light:
            self._upload_dir_light(model)
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
    def _upload_point_lights(model: Model) -> None:
        self = Renderer
        if self.point_lights and len(self.point_lights):
            model.shader['u_NPointLights'].write(
                glm.int32(len(self.point_lights)))
        for i in range(min(N_MAX_POINT_LIGHTS, len(self.point_lights))):
            point_light = self.point_lights[i]
            name = f'u_PointLights[{i}]'
            model.shader[name + '.linear'].write(point_light.linear)
            model.shader[name + '.quadratic'].write(point_light.quadratic)
            model.shader[name + '.position'].write(point_light.position)
            model.shader[name + '.ambient'].write(point_light.ambient)
            model.shader[name + '.diffuse'].write(point_light.diffuse)
            model.shader[name + '.specular'].write(point_light.specular)

    @staticmethod
    def _upload_dir_light(model: Model) -> None:
        self = Renderer
        model.shader['u_DirLight.direction'].write(self.dir_light.direction)
        model.shader['u_DirLight.ambient'].write(self.dir_light.ambient)
        model.shader['u_DirLight.diffuse'].write(self.dir_light.diffuse)
        model.shader['u_DirLight.specular'].write(self.dir_light.specular)
