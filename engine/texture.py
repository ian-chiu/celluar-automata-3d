from typing import Tuple
import glm
import moderngl as mgl
from moderngl import Texture, TextureCube
from pathlib import Path
import pygame as pg
import engine.gl as gl


def get_white_texture():
    self = get_white_texture
    if not hasattr(self, 'white'):
        self.white = gl.ctx.texture(size=(1, 1),
                                    components=4,
                                    data=bytearray([255] * 4))
    return self.white

def get_depth_texture(
        scale: float,
        window_size: Tuple[float, float]) -> Texture:
    depth_texture = gl.ctx.depth_texture(glm.ivec2(window_size) * scale)
    # depth_texture.compare_func = ''
    depth_texture.repeat_x = False
    depth_texture.repeat_y = False
    # depth_texture.filter = mgl.LINEAR, mgl.LINEAR
    return depth_texture

def load_texture_cube(dir_path: Path, ext='png') -> TextureCube:
    faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
    textures = []
    for face in faces:
        texture = pg.image.load(dir_path / f'{face}.{ext}').convert()
        if face in ['right', 'left', 'front', 'back']:
            texture = pg.transform.flip(texture, flip_x=True, flip_y=False)
        else:
            texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        textures.append(texture)
    size = textures[0].get_size()
    texture_cube = gl.ctx.texture_cube(size=size, components=3, data=None)
    for i in range(6):
        texture_data = pg.image.tostring(textures[i], 'RGB')
        texture_cube.write(face=i, data=texture_data)
    return texture_cube

def load_texture(path: Path) -> Texture:
    texture = pg.image.load(path).convert()
    texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
    texture = gl.ctx.texture(size=texture.get_size(), components=3,
                          data=pg.image.tostring(texture, 'RGB'))
    texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
    texture.build_mipmaps()
    texture.anisotropy = 32.0
    return texture
