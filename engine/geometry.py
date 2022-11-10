import numpy as np
import engine.gl as gl

class BaseGeometry:
    def __init__(self, format: str, attributes: list[str]):
        self.format = format
        self.attributes = attributes
        self.buffer = self._get_buffer()

    def _get_buffer(self):
        return gl.ctx.buffer()

class BoxGeometry(BaseGeometry):
    def __init__(self):
        format = '3f 2f 3f'
        attributes = ['a_Position', 'a_UV', 'a_Normal']
        super().__init__(format, attributes)

    def _get_data(self, positions, indices):
        data = [positions[i] for triangle in indices for i in triangle]
        return np.array(data, dtype='float32')

    def _get_buffer(self):
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        positions = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                     (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        vertex_data = self._get_data(positions, indices)

        uv_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        uv_indices = [(0, 2, 3), (0, 1, 2),
                      (0, 2, 3), (0, 1, 2),
                      (0, 1, 2), (2, 3, 0),
                      (2, 3, 0), (2, 0, 1),
                      (0, 2, 3), (0, 1, 2),
                      (3, 1, 2), (3, 0, 1),]
        uv_data = self._get_data(uv_vertices, uv_indices)

        normals = [( 0, 0, 1) * 6,
                   ( 1, 0, 0) * 6,
                   ( 0, 0,-1) * 6,
                   (-1, 0, 0) * 6,
                   ( 0, 1, 0) * 6,
                   ( 0,-1, 0) * 6,]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        vertex_data = np.hstack([vertex_data, uv_data])
        vertex_data = np.hstack([vertex_data, normals])
        return gl.ctx.buffer(vertex_data)

class EnvBoxGemoetry(BaseGeometry):
    def __init__(self):
        super().__init__('3f', ['a_Position'])

    def _get_data(self, positions, indices):
        data = [positions[i] for triangle in indices for i in triangle]
        return np.array(data, dtype='float32')

    def _get_buffer(self):
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        positions = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                     (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        vertex_data = self._get_data(positions, indices)
        vertex_data = np.flip(vertex_data, 1).copy(order='C')
        return gl.ctx.buffer(vertex_data)
