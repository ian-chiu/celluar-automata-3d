from typing import Optional
import moderngl as mgl
from moderngl import Context

ctx: Optional[Context] = None


class GLUtils:
    @staticmethod
    def set_context():
        global ctx
        ctx = mgl.create_context()
