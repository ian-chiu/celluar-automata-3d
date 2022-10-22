import glm

class Camera:
    def __init__(
            self,
            fov: float = 45.0,
            aspect: float = 16/9,
            near: float = 0.1,
            far: float = 150):
        self._aspect = aspect
        self._fov = fov
        self._near = near
        self._far = far
        self._position = glm.vec3(0, 0, 10)
        self._front = glm.vec3(0, 0, -1)
        self._up = glm.vec3(0, 1, 0)
        self._pitch = 0.0
        self._yaw = -89.0
        self._view_matrix = glm.mat4()
        self._proj_matrix = glm.mat4()
        self.view_proj_matrix = glm.mat4()
        self.recalculate_view_matrix()
        self.recalculate_proj_matrix()

    def recalculate_view_matrix(self):
        direction = glm.vec3()
        direction.x = glm.cos(glm.radians(self._yaw)) \
                      * glm.cos(glm.radians(self._pitch))
        direction.y = glm.sin(glm.radians(self._pitch))
        direction.z = glm.sin(glm.radians(self._yaw)) \
                      * glm.cos(glm.radians(self._pitch))
        self._front = glm.normalize(direction)
        self._view_matrix = glm.lookAt(self._position,
                                       self._position + self._front, self._up)
        self.view_proj_matrix = self._proj_matrix * self._view_matrix

    def recalculate_proj_matrix(self):
        self._proj_matrix = glm.perspective(self._fov, self._aspect,
                                            self._near, self._far)
        self.view_proj_matrix = self._proj_matrix * self._view_matrix

    def focus(self, focus_position: glm.vec3):
        self._view_matrix = glm.lookAt(self._position,
                                       focus_position, self._up)
        self.view_proj_matrix = self._proj_matrix * self._view_matrix

    @property
    def view_matrix(self):
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, view_matrix: glm.mat4):
        self._view_matrix = view_matrix
        self.view_proj_matrix = self._proj_matrix * self._view_matrix

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position: glm.vec3):
        self._position = position
        self.recalculate_view_matrix()

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, yaw: float):
        self._yaw = yaw
        self.recalculate_view_matrix()

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, pitch: float):
        self._pitch = pitch
        self._pitch = min(self._pitch, 89.0)
        self._pitch = max(self._pitch, -89.0)
        self.recalculate_view_matrix()

    @property
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, aspect):
        self._aspect = aspect
        self.recalculate_proj_matrix()

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, fov):
        self._fov = fov
        self.recalculate_proj_matrix()
