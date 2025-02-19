from OpenGL import GL
import glm

from interface.renderer.mesh import MeshBuffer, MeshHandle, Mesh
from interface.renderer.material import Material, UniformLocations, ShaderRegistry
from interface.renderer.scene_graph import SceneNode, Transform, RenderingInfo
from interface.renderer.camera import Camera



class RendererContext:
    current_shader : int = -1
    current_material : Material = None
    scene_root : SceneNode = None
    mesh_buffer : MeshBuffer = None
    renderer_locations : UniformLocations = None
    camera : Camera = None
    shader_registry : ShaderRegistry = None

    def __init__(self):
        self.current_shader = -1
        self.current_material = None
        self.scene_root = SceneNode.empty_node("Root")
        self.mesh_buffer = MeshBuffer()
        self.renderer_locations = None
        self.camera = Camera.default()
        self.shader_registry = ShaderRegistry()

    def add_mesh(self, mesh : Mesh, mesh_name : str):
        self.mesh_buffer.add_mesh(mesh, mesh_name)

    def add_mesh_from_file(self, file_path : str, mesh_name : str):
        mesh = Mesh.from_obj(file_path)
        self.add_mesh(mesh, mesh_name)

    def add_node(self, mesh_name : str, material : Material, transform : glm.mat4, parent : SceneNode):
        mesh_handle = self.mesh_buffer.get_handle(mesh_name)
        rendering_info = RenderingInfo(transform, material, mesh_handle)
        node = SceneNode(mesh_name, rendering_info)
        if parent is None:
            return self.scene_root.add_child(node)

        return parent.add_child(node)

    def pass_camera_uniforms(self):
        projection = self.camera.get_projection_matrix()
        view = self.camera.transform.get_matrix()
        GL.glUniformMatrix4fv(self.renderer_locations.projection, 1, GL.GL_FALSE, glm.value_ptr(projection))
        GL.glUniformMatrix4fv(self.renderer_locations.view, 1, GL.GL_FALSE, glm.value_ptr(view))

class Renderer:
    def __init__(self):
        self.context = RendererContext()
        self.mesh_dirty = True

    def bind_buffer(self):
        self.context.mesh_buffer.bind()
        self.mesh_dirty = False

    def add_child(self, mesh_name : str, material : Material, transform : glm.mat4, parent : SceneNode=None):
        return self.context.add_node(mesh_name, material, transform, parent)
    
    def add_mesh(self, mesh : Mesh, mesh_name : str):
        self.context.add_mesh(mesh, mesh_name)
        self.mesh_dirty = True

    def render(self):
        if self.mesh_dirty:
            self.bind_buffer()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.context.scene_root.traverse(self.render_node)

    def render_node(self, node : SceneNode, current_transform : glm.mat4, level : int):
        if MeshHandle.is_empty(node.rendering_info.mesh_handle):
            return

        rendering_info = node.rendering_info
        material = rendering_info.material
        mesh_handle = rendering_info.mesh_handle
        material.apply(self.context)
        self.render_mesh(mesh_handle, current_transform)

    def render_mesh(self, mesh_handle : MeshHandle, transform : glm.mat4):
        if MeshHandle.is_empty(mesh_handle):
            return
        # print(f"Rendering mesh from {mesh_handle.starting_index} to {mesh_handle.ending_index}")
        GL.glUniformMatrix4fv(self.context.renderer_locations.model, 1, GL.GL_FALSE, glm.value_ptr(transform))
        GL.glDrawElements(GL.GL_TRIANGLES, mesh_handle.index_count, GL.GL_UNSIGNED_INT, mesh_handle.starting_index)
