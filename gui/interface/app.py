import sys
from PyQt5 import QtWidgets
from PyQt5 import QtOpenGL
from OpenGL import GL

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

class AppInterface:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        self.gl_widget = OpenGLWidget()
        self.window.setCentralWidget(self.gl_widget)
        self.window.setGeometry(100, 100, 600, 400)
        self.window.setWindowTitle("OpenGL Triangle")
        self.window.show()

    def tick(self):
        self.app.processEvents()