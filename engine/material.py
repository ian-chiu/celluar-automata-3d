from typing import Optional
import glm
import numpy as np
from pathlib import Path
from enum import IntEnum
from engine.shader import Shader
from engine.texture import load_texture, get_white_texture


class BaseMaterial:
    def __init__(self):
        self.shader = Shader.flat

    def use(self):
        pass


class FlatMaterial(BaseMaterial):
    def __init__(
            self,
            texture_src: Optional[Path] = None,
            color = (1, 1, 1, 1),
            ) -> None:
        super().__init__()
        self.shader = Shader.flat
        self.texture = get_white_texture() if not texture_src \
             else load_texture(texture_src)
        self.color = glm.vec4(color)

    def use(self):
        self.texture.use()
        if not self.shader:
            return
        self.shader['u_Color'].write(self.color)


class PhongMaterial(BaseMaterial):
    def __init__(
            self,
            diffuse_src: Optional[Path] = None,
            specular_src: Optional[Path] = None,
            color: list[float] = [1, 1, 1],
            shininess = 32.0
            ) -> None:
        super().__init__()
        self.shader = Shader.phong
        white_texture = get_white_texture()
        self.diffuse = white_texture if not diffuse_src \
             else load_texture(diffuse_src)
        self.specular = white_texture if not specular_src \
             else load_texture(specular_src)
        self.color = glm.vec3(color)
        self.shininess = np.float32(shininess)

    def use(self):
        self.diffuse.use(self.TextureSlot.Diffuse)
        self.specular.use(self.TextureSlot.Specular)
        if not self.shader:
            return
        self.shader['u_Material.diffuse'].write(
            np.int32(self.TextureSlot.Diffuse))
        self.shader['u_Material.specular'].write(
            np.int32(self.TextureSlot.Specular))
        self.shader['u_Material.color'].write(self.color)
        self.shader['u_Material.shininess'].write(self.shininess)

    class TextureSlot(IntEnum):
        Diffuse = 0
        Specular = 1
