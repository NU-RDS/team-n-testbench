from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from OpenGL import GL
from PyQt5 import QtWidgets, QtOpenGL
import glm

from interface.dock import dock, BaseDockWidget, ImmediateInspectorDock
from interface.renderer.renderer import Renderer
from interface.renderer.material import Material, MaterialProperties
from interface.renderer.scene_graph import SceneNode, Transform
from interface.renderer.mesh import Mesh, MeshHandle
from util.path import PathUtil

import random

class OpenGLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.renderer = Renderer()

    def initializeGL(self):
        GL.glClearColor(0.1, 0.2, 0.25, 1.0)
        self.renderer.add_mesh(
            Mesh.from_obj_file(PathUtil.asset_file_path("meshes/crystal.obj")), "crystal"
        )

        position_magnitude = 100
        scale_magnitude = 10

        for i in range(1000):
            random_position = glm.vec3(
                random.uniform(-position_magnitude, position_magnitude),
                random.uniform(-position_magnitude, position_magnitude),
                random.uniform(-position_magnitude, position_magnitude),
            )

            random_scale = glm.vec3(
                random.uniform(0, scale_magnitude),
                random.uniform(0, scale_magnitude),
                random.uniform(0, scale_magnitude),
            )

            self.renderer.add_child(
                "crystal",
                Material.base_color(self.renderer.context, glm.vec3(1.0, 0.0, 0.0)),
                Transform().
                    set_position(random_position).
                    set_scale(random_scale)
            )


    def resizeGL(self, width, height):
        pass

    def paintGL(self):
        self.renderer.render()


@dock("Simulation")
class SimulationDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("OpenGL Dock", parent)
        self.main_widget = OpenGLWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
