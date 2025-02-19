import glm
from OpenGL import GL

from interface.renderer.renderer import RendererLocations
from util.path import PathUtil


class ShaderPair:
    def __init__(self, vertex_shader: str, fragment_shader: str):
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader

    def compile(self):
        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertex_shader, self.vertex_shader)
        GL.glCompileShader(vertex_shader)

        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragment_shader, self.fragment_shader)
        GL.glCompileShader(fragment_shader)

        shader_program = GL.glCreateProgram()
        GL.glAttachShader(shader_program, vertex_shader)
        GL.glAttachShader(shader_program, fragment_shader)
        GL.glLinkProgram(shader_program)

        return shader_program


class ShaderRegistry:
    shaders = {}
    shader_ids = {}

    def __init__(self):
        self.shaders = {}
        self.shader_ids = {}

    @staticmethod
    def register(self, vertex_shader_path: str, fragment_shader_path: str):
        if (vertex_shader_path, fragment_shader_path) in self.shaders:
            return self.shaders[(vertex_shader_path, fragment_shader_path)]

        with open(vertex_shader_path, "r") as file:
            vertex_shader = file.read()

        with open(fragment_shader_path, "r") as file:
            fragment_shader = file.read()

        shader_pair = ShaderPair(vertex_shader, fragment_shader)
        shader_program = shader_pair.compile()
        self.shaders[(vertex_shader_path, fragment_shader_path)] = shader_program
        self.shader_ids[shader_program] = shader_pair

    @staticmethod
    def get(self, shader_id: int) -> ShaderPair:
        if shader_id not in self.shader_ids:
            return None

        return self.shader_ids[shader_id]


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
            rendering_context.pass_camera_uniforms()

        GL.glUniform3f(
            GL.glGetUniformLocation(self.shader, "u_color"),
            self.properties.color.x,
            self.properties.color.y,
            self.properties.color.z,
        )

    @staticmethod
    def base_color(color: glm.vec3) -> "Material":
        properties = MaterialProperties()
        properties.color = color

        return Material(
            ShaderRegistry.get(
                PathUtil.asset_file_path("shaders/base.vert"),
                PathUtil.asset_file_path("shaders/base.frag"),
            ),
            properties,
        )
