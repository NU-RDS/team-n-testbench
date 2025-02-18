from OpenGL import GL
import numpy as np

class Vertex:
    def __init__(self, position : np.array, color : np.array):
        self.position = position
        self.color = color

    def add_to_vbo(self, vbo : list):
        vbo.extend(self.position)
        vbo.extend(self.color)

class Mesh:
    def __init__(self, vertices : list[Vertex], indices : list[int]):
        self.vertices = vertices
        self.indices = indices

    def add_to_buffer(self, vbos : list, ibos : list):
        for vertex in self.vertices:
            vertex.add_to_vbo(vbos)

        ibos.extend(self.indices)

class MeshHandle:
    def __init__(self, starting_index : int, index_count : int):
        self.starting_index = starting_index
        self.index_count = index_count

    @staticmethod
    def is_empty(mesh_handle : "MeshHandle"):
        return mesh_handle.index_count == 0
    
    @staticmethod
    def make_empty():
        return MeshHandle(0, 0)

class MeshBuffer:
    def __init__(self):
        self.mesh_vbos = []
        self.mesh_ibos = []
        self.mesh_handles = {} # key is the mesh name, value is the mesh handle

    def add_mesh(self, mesh : Mesh, mesh_name : str):
        starting_index = len(self.mesh_ibos)
        mesh.add_to_buffer(self.mesh_vbos, self.mesh_ibos)
        index_count = len(self.mesh_ibos) - starting_index
        self.mesh_handles[mesh_name] = MeshHandle(starting_index, index_count)

class MaterialProperties:
    def __init__(self):
        self.shader = 0
        self.color = np.array([0.0, 0.0, 0.0])

class Material:
    def __init__(self, shader : int, properties : MaterialProperties):
        self.shader = shader
        self.properties = properties

class Transform:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        # should be a quaternion
        self.rotation = np.array([0.0, 0.0, 0.0, 1.0])
        self.scale = np.array([1.0, 1.0, 1.0])

    def get_matrix(self):
        # form a transformation matrix from the position, rotation, and scale
        # the matrix should be a 4x4 matrix
        return np.identity(4)


class RenderingInfo:
    def __init__(self, transform : Transform, material : Material, mesh_handle : MeshHandle):
        self.transform = transform
        self.material = material
        self.mesh_handle = mesh_handle

class SceneNode:
    def __init__(self, name : str, render_info : RenderingInfo):
        self.name = name
        self.children = []
        self.rendering_info = render_info

    def add_child(self, child : "SceneNode"):
        self.children.append(child)


    def _traverse_helper(self, callback, parent_transform : np.matrix, level : int):
        pass


    def traverse(self, callback):
        self._traverse_helper(callback, np.identity(4), 0)
