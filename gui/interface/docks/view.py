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
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
        self.last_mouse_pos = (
            None  # Store the last mouse position for delta computation
        )

    def initializeGL(self):
        self.renderer.add_mesh(
            Mesh.from_obj_file(PathUtil.asset_file_path("meshes/crystal.obj")),
            "crystal",
        )

        grid_size = 1000
        self.renderer.add_mesh(Grid.create_grid_data(grid_size, 0.5), "grid")

        # Create a grid node with GL_LINES draw mode.
        self.renderer.add_child(
            "grid",
            Material.base_color(
                self.renderer.context, glm.vec3(0.0, 1.0, 1.0), fade=True
            ),
            Transform().set_scale(glm.vec3(1.0, 1.0, 1.0)),
            draw_mode=GL.GL_LINES,
        )

        position_magnitude = 100
        scale_magnitude = 10
        red_material = Material.base_color(
            self.renderer.context, glm.vec3(1.0, 0.0, 0.0)
        )

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
                Transform().set_position(random_position).set_scale(random_scale),
            )

        self.renderer.begin_rendering()

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)

    def paintGL(self):
        aspect_ratio = self.width() / self.height()
        self.renderer.context.camera.update_aspect_ratio(aspect_ratio)
        self.renderer.render()
        GL.glGetError()

    # --- Mouse & Wheel Event Handlers for Camera Control ---
    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return

        delta = event.pos() - self.last_mouse_pos
        self.last_mouse_pos = event.pos()

        # Left mouse button: rotate (orbit) camera.
        if event.buttons() & Qt.LeftButton:
            # Adjust sensitivity as needed.
            sensitivity = 0.5
            angle_x = sensitivity * delta.y()  # Rotate up/down
            angle_y = sensitivity * delta.x()  # Rotate left/right

            # Create rotation quaternions (note: glm.angleAxis expects angles in radians)
            rot_x = glm.angleAxis(glm.radians(angle_x), glm.vec3(1, 0, 0))
            rot_y = glm.angleAxis(glm.radians(angle_y), glm.vec3(0, 1, 0))
            # Update camera's rotation. The new rotation is applied before the existing rotation.
            self.renderer.context.camera.transform.rotation = (
                rot_y * rot_x * self.renderer.context.camera.transform.rotation
            )
            self.update()

        # Right mouse button: pan camera.
        elif event.buttons() & Qt.RightButton:
            pan_speed = 0.01
            # Invert X delta for natural panning.
            pan_delta = glm.vec3(-delta.x() * pan_speed, delta.y() * pan_speed, 0)
            self.renderer.context.camera.transform.position += pan_delta
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        # Zoom: adjust the camera's Z position.
        zoom_speed = 0.001
        delta = event.angleDelta().y()
        self.renderer.context.camera.transform.position.z += delta * zoom_speed
        self.update()


@dock("Simulation")
class SimulationDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("OpenGL Dock", parent)
        self.main_widget = OpenGLWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
