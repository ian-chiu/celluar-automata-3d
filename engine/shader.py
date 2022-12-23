from typing import Optional
from moderngl import Program
import engine.gl as gl


class Shader:
    flat: Optional[Program] = None
    phong: Optional[Program] = None
    phong_batch: Optional[Program] = None
    background: Optional[Program] = None

    @staticmethod
    def init():
        self = Shader
        Shader.flat = self.load('flat')
        Shader.phong = self.load('phong')
        Shader.background = self.load('background')

    @staticmethod
    def shutdown():
        self = Shader
        if self.flat:
            self.flat.release()
        if self.phong:
            self.phong.release()
        if self.background:
            self.background.release()

    @staticmethod
    def load(filename: str) -> Program:
        if not gl.ctx:
            raise RuntimeError("Application has not create gl context yet!")
        with open(f'assets/shaders/{filename}.glsl') as file:
            lines = file.readlines()
            line_index = 0
            vertex_source = ""
            fragment_source = ""
            while line_index < len(lines):
                if "VERTEX_SHADER" in lines[line_index]:
                    line_index += 1
                    while "endif" not in lines[line_index]:
                        vertex_source += lines[line_index]
                        line_index += 1
                elif "FRAGMENT_SHADER" in lines[line_index]:
                    line_index += 1
                    while "endif" not in lines[line_index]:
                        fragment_source += lines[line_index]
                        line_index += 1
                line_index += 1

        version_heading = "#version 330 core\n"
        vertex_heading = "#define VERTEX_SHADER\n"
        vertex_shader = version_heading + vertex_heading + vertex_source
        fragment_heading = "#define FRAGMENT_SHADER\n"
        fragment_shader = version_heading + fragment_heading + fragment_source
        program = gl.ctx.program(vertex_shader=vertex_shader,
                                 fragment_shader=fragment_shader)
        return program
