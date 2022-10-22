import pygame as pg
import numpy as np
from moderngl import Context, Program, VertexArray
from engine.vbo import BaseVbo

def get_vao(ctx: Context, program: Program, vbo: BaseVbo) -> VertexArray:
    vao = ctx.vertex_array(program,
                           [(vbo.vbo, vbo.format, *vbo.attributes)],
                           skip_errors=True)
    return vao

def load_shader(ctx: Context, filename: str) -> Program:
    with open(f'shaders/{filename}.glsl') as file:
        shader_source = file.read()
    version_heading = "#version 330 core\n"
    vertex_heading = "#define VERTEX_SHADER\n"
    vertex_shader = version_heading + vertex_heading + shader_source
    fragment_heading = "#define FRAGMENT_SHADER\n"
    fragment_shader = version_heading + fragment_heading + shader_source
    program = ctx.program(vertex_shader=vertex_shader,
                          fragment_shader=fragment_shader)
    return program

def is_key_pressed(key: int):
    pressed = np.array(pg.key.get_pressed(), dtype="bool")
    repeated = np.array(pg.key.get_repeat(), dtype="bool")
    detected = np.logical_and(pressed, repeated)
    return detected[key - 1]

def is_mouse_pressed(button: int):
    pressed = pg.mouse.get_pressed()
    return pressed[button - 1]
