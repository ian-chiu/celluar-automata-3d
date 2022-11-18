from typing import List
import glm
import numpy as np

class Light:
    def __init__(
            self,
            ambient: List[float] = [1, 1, 1],
            diffuse: List[float] = [1, 1, 1],
            specular: List[float] = [1, 1, 1]
            ) -> None:
        self.ambient = glm.vec3(ambient)
        self.diffuse = glm.vec3(diffuse)
        self.specular = glm.vec3(specular)

class PointLight(Light):
    def __init__(
            self,
            ambient: List[float] = [1, 1, 1],
            diffuse: List[float] = [1, 1, 1],
            specular: List[float] = [1, 1, 1],
            position: List[float] = [0, 0, 0],
            linear: float = 0.09,
            quadratic: float = 0.032
            ) -> None:
        super().__init__(ambient, diffuse, specular)
        self.position = glm.vec3(position)
        self.linear = np.float32(linear)
        self.quadratic = np.float32(quadratic)

class DirLight(Light):
    def __init__(
            self,
            ambient: List[float] = [1, 1, 1],
            diffuse: List[float] = [1, 1, 1],
            specular: List[float] = [1, 1, 1],
            direction: List[float] = [0, 0, 0],
            ) -> None:
        super().__init__(ambient, diffuse, specular)
        self.direction = glm.vec3(direction)

class SpotLight(Light):
    def __init__(
            self,
            ambient: List[float] = [1, 1, 1],
            diffuse: List[float] = [1, 1, 1],
            specular: List[float] = [1, 1, 1],
            position: List[float] = [0, 0, 0],
            direction: List[float] = [0, 0, 0],
            cutoff: float = 0.09,
            ) -> None:
        super().__init__(ambient, diffuse, specular)
        self.direction = glm.vec3(direction)
        self.position = glm.vec3(position)
        self.cutoff = np.float32(cutoff)
