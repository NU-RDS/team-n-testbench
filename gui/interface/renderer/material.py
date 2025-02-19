import glm
from OpenGL import GL

from interface.renderer.renderer import RendererLocations


class MaterialProperties:
    def __init__(self):
        self.shader = 0
        self.color = glm.vec3(0.0, 0.0, 0.0)  # Using glm.vec3 for color


class Material:
    def __init__(self, shader: int, properties: MaterialProperties):
        self.shader = shader
        self.properties = properties

    def apply(self, rendering_context):
        if rendering_context.current_material == self:
            return

        rendering_context.current_material = self

        if rendering_context.current_shader != self.shader:
            self.active_shader = self.shader
            GL.glUseProgram(self.shader)
            rendering_context.renderer_locations = RendererLocations(self.shader)

        GL.glUniform3f(
            GL.glGetUniformLocation(self.shader, "color"),
            self.properties.color.x,
            self.properties.color.y,
            self.properties.color.z,
        )
