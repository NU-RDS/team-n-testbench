import glm
from OpenGL import GL

from util.path import PathUtil

class UniformLocations:
    def __init__(self, shader):
        self.color = GL.glGetUniformLocation(shader, "u_color")
        self.model = GL.glGetUniformLocation(shader, "u_model")
        self.view = GL.glGetUniformLocation(shader, "u_view")
        self.projection = GL.glGetUniformLocation(shader, "u_projection")

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

        print(GL.glGetProgramInfoLog(shader_program))

        return shader_program

class ShaderRegistry:
    keys_to_shader_ids = {}
    shader_ids_to_pair = {}

    def __init__(self):
        self.keys_to_shader_ids = {}
        self.shader_ids_to_pair = {}

    def _generate_shader_key(self, vertex_shader_path: str, fragment_shader_path: str) -> str:
        return f"{vertex_shader_path},{fragment_shader_path}"

    def register(self, vertex_shader_path: str, fragment_shader_path: str) -> int:
        # does this shader pair already exist?
        key = self._generate_shader_key(vertex_shader_path, fragment_shader_path)
        if key in self.keys_to_shader_ids:
            return self.keys_to_shader_ids[key]

        shader_pair = ShaderPair(
            PathUtil.read_file(vertex_shader_path),
            PathUtil.read_file(fragment_shader_path),
        )
        shader_id = shader_pair.compile()
        print(f"Registered shader pair {key} with id {shader_id}")
        self.keys_to_shader_ids[key] = shader_id
        self.shader_ids_to_pair[shader_id] = shader_pair

        return shader_id

    def get_from_paths(self, vertex_shader_path: str, fragment_shader_path: str) -> int:
        if (vertex_shader_path, fragment_shader_path) not in self.keys_to_shader_ids:
            return self.register(vertex_shader_path, fragment_shader_path)

        return self.keys_to_shader_ids[self._generate_shader_key(vertex_shader_path, fragment_shader_path)]

    def get(self, shader_id: int) -> ShaderPair:
        print(self.shader_ids_to_pair.keys())
        if shader_id not in self.shader_ids_to_pair.keys():
            return None

        return self.shader_ids_to_pair[shader_id]


class MaterialProperties:
    def __init__(self):
        self.shader = -1
        self.color = glm.vec3(0.0, 0.0, 0.0)  # Using glm.vec3 for color


class Material:
    def __init__(self, shader: int, properties: MaterialProperties):
        self.shader = shader
        self.properties = properties

    def apply(self, rendering_context):
        if rendering_context.current_material == self:
            return

        print("Swapping to material with shader", self.shader)
        rendering_context.current_material = self

        if rendering_context.current_shader != self.shader:
            print("Switching shader to", self.shader)
            rendering_context.current_shader = self.shader
            GL.glUseProgram(self.shader)
            rendering_context.renderer_locations = UniformLocations(self.shader)
            rendering_context.pass_camera_uniforms()

        GL.glUniform3f(
            rendering_context.renderer_locations.color,
            self.properties.color.x,
            self.properties.color.y,
            self.properties.color.z,
        )

    @staticmethod
    def base_color(rendering_context, color: glm.vec3) -> "Material":
        properties = MaterialProperties()
        properties.color = color

        return Material(
            rendering_context.shader_registry.get_from_paths(
                PathUtil.asset_file_path("shaders/vert.glsl"),
                PathUtil.asset_file_path("shaders/frag.glsl"),
            ),
            properties,
        )
