from moderngl import Context
import numpy as np

class BaseVbo:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format = "3f"
        self.attributes = ["a_Position"]

    def get_vertex_data(self):
        ...

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def destroy(self):
        self.vbo.release()


class TriangleVbo(BaseVbo):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attributes = ['a_Position']

    def get_vertex_data(self):
        positions = [(-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.0, 0.5, 0.0)]
        return np.array(positions, dtype='float32')


class CubeVbo(BaseVbo):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 2f 3f'
        self.attributes = ['a_Position', 'a_UV', 'a_Normal']

    @staticmethod
    def get_data(positions, indices):
        data = [positions[i] for triangle in indices for i in triangle]
        return np.array(data, dtype='float32')

    def get_vertex_data(self):
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        positions = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                     (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        vertex_data = self.get_data(positions, indices)

        uv_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        uv_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2),
                             (0, 1, 2), (2, 3, 0),
                             (2, 3, 0), (2, 0, 1),
                             (0, 2, 3), (0, 1, 2),
                             (3, 1, 2), (3, 0, 1),]
        uv_data = self.get_data(uv_vertices, uv_indices)

        normals = [( 0, 0, 1) * 6,
                   ( 1, 0, 0) * 6,
                   ( 0, 0,-1) * 6,
                   (-1, 0, 0) * 6,
                   ( 0, 1, 0) * 6,
                   ( 0,-1, 0) * 6,]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        vertex_data = np.hstack([vertex_data, uv_data])
        vertex_data = np.hstack([vertex_data, normals])
        return vertex_data
