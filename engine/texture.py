from typing import Tuple, List
import glm
import moderngl as mgl
from moderngl import Texture, TextureCube
from pathlib import Path
import engine.gl as gl
from PIL import Image, ImageOps

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
    textures: List[Image.Image] = []
    for face in faces:
        texture = Image.open(dir_path / f'{face}.{ext}')
        if face in ['right', 'left', 'front', 'back']:
            texture = ImageOps.mirror(texture)
        else:
            texture = ImageOps.flip(texture)
        textures.append(texture)
    size = textures[0].get_size()
    texture_cube = gl.ctx.texture_cube(size=size, components=3, data=None)
    for i in range(6):
        texture_data = textures[i].tobytes("raw", "RGB")
        texture_cube.write(face=i, data=texture_data)
    return texture_cube

def load_texture(path: Path) -> Texture:
    texture = Image.open(path)
    texture = ImageOps.flip(texture)
    texture = gl.ctx.texture(size=texture.get_size(), components=3,
                             data=texture.tobytes("raw", "RGB"))
    texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
    texture.build_mipmaps()
    texture.anisotropy = 32.0
    return texture
