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

class OpenGLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.renderer = Renderer()

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.renderer.add_mesh(
            Mesh.from_obj(PathUtil.get_resource("crystal.obj")), "crystal"
        )

        self.renderer.add_child(
            "crystal",
            Material.base_color(glm.vec3(1.0, 0.0, 0.0)),
            Transform()
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
