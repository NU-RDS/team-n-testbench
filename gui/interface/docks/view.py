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
from app_context import ApplicationContext
import time
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

        self.base_node = None
        self.link_1_node = None
        self.link_2_node = None

        self.camera_distance = 15
        self.camera_angle = 0.0



    def initializeGL(self):
        needed_meshes = ["crystal", "base", "link_1", "link_2"]
        for mesh_name in needed_meshes:
            self.renderer.add_mesh(Mesh.from_obj_file(PathUtil.asset_file_path(f"meshes/{mesh_name}.obj")), mesh_name)

        red_material = Material.base_color(
            self.renderer.context, glm.vec3(0.8, 0.1, 0.15)
        )

        blue_material = Material.base_color(
            self.renderer.context, glm.vec3(0.15, 0.1, 0.9)
        )

        green_material = Material.base_color(
            self.renderer.context, glm.vec3(0.15, 0.9, 0.1)
        )

        # add the base
        scale_axis = 10.0
        self.base_node = self.renderer.add_child(
            "base",
            red_material,
            Transform().set_position(glm.vec3(0, -3, 0)).set_scale(glm.vec3(scale_axis, scale_axis, scale_axis)),
        )

        # as a parent of the base, add the first link
        self.link_1_node = self.renderer.add_child(
            "link_1",
            blue_material,
            Transform().set_position(glm.vec3(0, .05, -0.2)),
            self.base_node
        )

        # as a parent of the first link, add the second link
        self.link_2_node = self.renderer.add_child(
            "link_2",
            green_material,
            Transform().set_position(glm.vec3(0, 0.05, -0.55)),
            self.link_1_node
        )

        self.renderer.begin_rendering()

    def set_camera_position(self, distance, angle):
        self.renderer.context.camera.transform.position = glm.vec3(
            distance * glm.sin(glm.radians(angle)),
            15,
            distance * glm.cos(glm.radians(angle)),
        )

        # make the camera look at the origin
        direction = glm.normalize(glm.vec3(0.0, 0.0, 0.0) - self.renderer.context.camera.transform.position)
        rot = glm.quatLookAt(direction, glm.vec3(0.0, 1.0, 0.0))
        self.renderer.context.camera.transform.rotation = rot


    def rotate_link(self, node_number, angle):
        if node_number == 0:
            node = self.link_1_node
        elif node_number == 1:
            node = self.link_2_node
        else:
            return

        node.rendering_info.transform.rotation = glm.angleAxis(glm.radians(angle), glm.vec3(1, 0, 0))

    def update_single_link(self, joint_number):
        datastream = ApplicationContext.telemetry.get_datastream(joint_number)
        if datastream is None:
            return
        
        latest = datastream.get_latest_snapshot()
        if latest is None:
            return
        
        self.rotate_link(joint_number, latest.joint_angle * 360)


    def update_scene(self):
        for i in range(0, 2):
            self.update_single_link(i)

        self.set_camera_position(self.camera_distance, time.time() * 10)


    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)

    def paintGL(self):
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

        self.timer_group.add_task(-1, self.main_widget.update_scene)
