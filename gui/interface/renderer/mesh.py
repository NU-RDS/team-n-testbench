import glm 
from OpenGL import GL
import numpy as np

class Vertex:
    def __init__(self, position: glm.vec3, normal: glm.vec3):
        self.position = position
        self.normal = normal

    def add_to_vbo(self, vbo: list):
        # Extend the VBO list with the components of position and color.
        # Using .x, .y, .z for glm.vec3 (for both position and color).
        vbo.extend([self.position.x, self.position.y, self.position.z])
        vbo.extend([self.normal.x, self.normal.y, self.normal.z])

    @staticmethod
    def set_vertex_attrib_pointers():
        # setup a_position attribute, and a_normal attribute
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * 4, None)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * 4, 12)

    @staticmethod
    def unset_vertex_attrib_pointers():
        # Unset the vertex attribute pointers for the VBO.
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)


class Mesh:
    def __init__(self, vertices: list, indices: list[int]):
        self.vertices = vertices  # List of Vertex objects
        self.indices = indices  # List of int

    def add_to_buffer(self, vbos: list, ibos: list):
        for vertex in self.vertices:
            vertex.add_to_vbo(vbos)
        ibos.extend(self.indices)

    @staticmethod
    def from_obj_file(file_path: str) -> "Mesh":
        """
        Load a mesh from an OBJ file.

        :param file_path: The path to the OBJ file.
        :return: A new Mesh object.
        """
        positions = []  # list of glm.vec3 for vertex positions
        normals = []  # list of glm.vec3 for vertex normals
        vertices = []  # final list of Vertex objects
        indices = []  # final list of indices
        vertex_map = {}  # maps (position_index, normal_index) to the final vertex index

        with open(file_path, "r") as file:
            for line in file:
                # Strip any whitespace at the ends.
                line = line.strip()
                if line.startswith("v "):
                    parts = line.split()
                    # Parse the x, y, z components.
                    pos = glm.vec3(float(parts[1]), float(parts[2]), float(parts[3]))
                    positions.append(pos)
                elif line.startswith("vn "):
                    parts = line.split()
                    norm = glm.vec3(float(parts[1]), float(parts[2]), float(parts[3]))
                    normals.append(norm)
                elif line.startswith("f "):
                    # Process face definitions.
                    # Faces may have more than 3 vertices (polygon). We'll triangulate them using a fan.
                    parts = line.split()[1:]
                    face_vertex_indices = []
                    for token in parts:
                        # The token can be in formats such as:
                        # "1" (only vertex position), "1/2" (position/texcoord),
                        # "1//3" (position//normal), or "1/2/3" (position/texcoord/normal)
                        splits = token.split("/")
                        pos_index = int(splits[0])
                        norm_index = None
                        if len(splits) >= 3 and splits[2] != "":
                            norm_index = int(splits[2])

                        # Use 0 as a placeholder key for missing normal
                        key = (pos_index, norm_index if norm_index is not None else 0)

                        # Check if we've already created this vertex.
                        if key not in vertex_map:
                            position = positions[pos_index - 1]
                            # If no normal is provided, use a default normal.
                            if norm_index is not None:
                                normal = normals[norm_index - 1]
                            else:
                                normal = glm.vec3(0.0, 0.0, 0.0)
                            new_vertex = Vertex(position, normal)
                            vertices.append(new_vertex)
                            vertex_map[key] = len(vertices) - 1
                        # Append the index for this vertex.
                        face_vertex_indices.append(vertex_map[key])

                    # Triangulate the face (assuming convex polygon using a fan)
                    if len(face_vertex_indices) >= 3:
                        for i in range(1, len(face_vertex_indices) - 1):
                            indices.extend(
                                [
                                    face_vertex_indices[0],
                                    face_vertex_indices[i],
                                    face_vertex_indices[i + 1],
                                ]
                            )
        return Mesh(vertices, indices)
    
    @staticmethod
    def multiple_from_obj_file(file_path: str) -> list["Mesh"]:
        """
        Load a mesh from an OBJ file.

        :param file_path: The path to the OBJ file.
        :return: A list of new Mesh objects.
        """
        contents = ""
        with open(file_path, "r") as file:
            contents = file.read()
        mesh_strings = contents.split("o ")
        meshes = []
        for mesh_string in mesh_strings:
            if mesh_string == "":
                continue
            mesh = Mesh.from_obj_string(mesh_string)
            meshes.append(mesh)
        return meshes
    


class MeshHandle:
    def __init__(self, starting_index: int, index_count: int):
        self.starting_index = starting_index
        self.index_count = index_count

    @staticmethod
    def is_empty(mesh_handle: "MeshHandle") -> bool:
        return mesh_handle.index_count == 0

    @staticmethod
    def make_empty() -> "MeshHandle":
        return MeshHandle(0, 0)
    
    @property
    def ending_index(self):
        return self.starting_index + self.index_count


class MeshBuffer:
    def __init__(self):
        self.mesh_vbos = []  # List of floats (vertex buffer)
        self.mesh_ibos = []  # List of ints (index buffer)
        self.mesh_handles = {}  # Dict mapping mesh names to MeshHandle objects

    def add_mesh(self, mesh: Mesh, mesh_name: str):
        starting_index = len(self.mesh_ibos)
        mesh.add_to_buffer(self.mesh_vbos, self.mesh_ibos)
        index_count = len(self.mesh_ibos) - starting_index
        self.mesh_handles[mesh_name] = MeshHandle(starting_index, index_count)

    # Optionally, you might add functions to retrieve buffers as arrays, etc.
    def get_vertex_buffer(self):
        return self.mesh_vbos

    def get_index_buffer(self):
        return self.mesh_ibos
    
    def get_handle(self, mesh_name: str) -> MeshHandle:
        if mesh_name not in self.mesh_handles:
            return MeshHandle.make_empty()
        return self.mesh_handles[mesh_name]
    
    def bind(self):
        """
        Create and bind the VAO, VBO, and IBO, and upload the mesh data to the GPU.
        """
        # Generate and bind a Vertex Array Object (VAO)
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        # Create and bind a Vertex Buffer Object (VBO)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        # Convert the list of floats into a numpy array of type float32.
        vertex_data = np.array(self.mesh_vbos, dtype=np.float32)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL.GL_STATIC_DRAW)

        # Create and bind an Index Buffer Object (IBO or EBO)
        self.ibo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        # Convert the list of indices into a numpy array of type uint32.
        index_data = np.array(self.mesh_ibos, dtype=np.uint32)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL.GL_STATIC_DRAW)

        # Setup the vertex attribute pointers.
        # Here, attribute location 0 is for positions, and location 1 is for normals.
        Vertex.set_vertex_attrib_pointers()

        # Unbind the VAO (the element array buffer binding is stored in the VAO)
        GL.glBindVertexArray(0)