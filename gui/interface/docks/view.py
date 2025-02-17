from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from OpenGL import GL
from PyQt5 import QtWidgets, QtOpenGL

from interface.dock import dock, BaseDockWidget, ImmediateInspectorDock

class OpenGLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-1, 1, -1, 1, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.5, 0.0)
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(-0.5, -0.5, 0.0)
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.5, -0.5, 0.0)
        GL.glEnd()

@dock("OpenGL Dock")
class OpenGLDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("OpenGL Dock", parent)
        self.main_widget = OpenGLWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
