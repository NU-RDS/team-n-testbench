import glm

from interface.renderer.material import Material
from interface.renderer.mesh import MeshHandle

class Transform:
    def __init__(self):
        self.position = glm.vec3(0.0, 0.0, 0.0)
        # Use glm.quat for rotation.
        # Note: In GLM the identity quaternion is glm.quat(1, 0, 0, 0) (w, x, y, z).
        self.rotation = glm.quat(1, 0, 0, 0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

    def get_matrix(self) -> glm.mat4:
        """
        Constructs a 4x4 transformation matrix from position, rotation, and scale.
        The order is: Translation * Rotation * Scale.
        """
        # Create translation matrix.
        translation = glm.translate(glm.mat4(1.0), self.position)
        # Create rotation matrix from quaternion.
        rotation = glm.mat4_cast(self.rotation)
        # Create scaling matrix.
        scaling = glm.scale(glm.mat4(1.0), self.scale)
        return translation * rotation * scaling


class RenderingInfo:
    def __init__(
        self, transform: Transform, material: Material, mesh_handle: MeshHandle
    ):
        self.transform = transform
        self.material = material
        self.mesh_handle = mesh_handle


class SceneNode:
    def __init__(self, name: str, render_info: RenderingInfo):
        self.name = name
        self.rendering_info = render_info
        self.children = []

    @staticmethod
    def empty_node(name: str) -> "SceneNode":
        """
        Create an empty scene node with the given name.
        """
        return SceneNode(name, RenderingInfo(Transform(), Material(0, None), MeshHandle(0, 0)))

    def add_child(self, child: "SceneNode"):
        self.children.append(child)

    def _traverse_helper(self, callback, parent_transform: glm.mat4, level: int):
        """
        Recursively traverse the scene graph.

        :param callback: A function that takes (node, current_transform, level).
        :param parent_transform: The accumulated transformation matrix from parent nodes.
        :param level: The current depth level in the scene graph.
        """
        # Compute the local transformation matrix.
        local_transform = self.rendering_info.transform.get_matrix()
        # Combine with parent's transformation.
        current_transform = parent_transform * local_transform

        # Call the callback for the current node.
        callback(self, current_transform, level)

        # Recurse for each child.
        for child in self.children:
            child._traverse_helper(callback, current_transform, level + 1)

    def traverse(self, callback):
        """
        Begin traversal from this node with the identity transformation.
        """
        identity = glm.mat4(1.0)
        self._traverse_helper(callback, identity, 0)