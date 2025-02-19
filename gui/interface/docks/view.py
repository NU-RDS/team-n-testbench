from PyQt5.QtCore import Qt, QSettings, QTimer
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from OpenGL import GL
from PyQt5 import QtWidgets, QtOpenGL
import glm

from interface.dock import dock, BaseDockWidget, ImmediateInspectorDock
from interface.renderer.renderer import Renderer
from interface.renderer.material import Material, MaterialProperties
from interface.renderer.scene_graph import SceneNode, Transform
from interface.renderer.mesh import Mesh, MeshHandle, Grid
from util.path import PathUtil

import random

class OpenGLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = Renderer()

        # make a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def initializeGL(self):
        self.renderer.add_mesh(
            Mesh.from_obj_file(PathUtil.asset_file_path("meshes/crystal.obj")), "crystal"
        )

        grid_size = 1000

        self.renderer.add_mesh(
            Grid.create_grid_data(grid_size, 0.5), "grid"
        )

        position_magnitude = 100
        scale_magnitude = 10
        red_material = Material.base_color(self.renderer.context, glm.vec3(1.0, 0.0, 0.0))

        for i in range(100):
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
                red_material,
                Transform().
                    set_position(random_position).
                    set_scale(random_scale)
            )

        self.renderer.add_child(
            "grid",
            Material.base_color(self.renderer.context, glm.vec3(0.0, 1.0, 1.0), fade=True),
            Transform().set_scale(glm.vec3(1.0, 1.0, 1.0)),
            draw_mode=GL.GL_LINES
        )

        self.renderer.begin_rendering()


    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)


    def paintGL(self):
        # tell the camera about the new aspect ratio
        aspect_ratio = self.width() / self.height()
        self.renderer.context.camera.update_aspect_ratio(aspect_ratio)

        self.renderer.render()
        GL.glGetError()


@dock("Simulation")
class SimulationDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("OpenGL Dock", parent)
        self.main_widget = OpenGLWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
