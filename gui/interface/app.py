import sys
from PyQt5 import QtWidgets, QtOpenGL
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from OpenGL import GL

from util.path import PathUtil
from interface.dock import DockRegistry
import interface.docks as dock_modules
import inspect


# Your OpenGL widget (using QGLWidget for consistency)
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


# A custom dock widget that serves as a "frame" for any widget content.
class CustomDockWidget(QDockWidget):
    def __init__(self, title, contentWidget=None, parent=None):
        super().__init__(title, parent)
        # Allow the dock widget to be moved, floated, and closed.
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

        # If no content widget is provided, create a simple widget with a label.
        if contentWidget is None:
            contentWidget = QWidget()
            layout = QVBoxLayout()
            label = QLabel(f"Content for {title}")
            layout.addWidget(label)
            contentWidget.setLayout(layout)

        self.setWidget(contentWidget)


# Our main window contains the central OpenGL widget and several dockable frames.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Tendon Robotic Finger Control GUI")
        self.setGeometry(100, 100, 800, 600)
        # Create a menu to add new frames dynamically.
        self.setup_menus()

    def setup_menus(self):
        menubar = self.menuBar()
        viewMenu = menubar.addMenu("View")

        # find all of the dock classes and add them to the menu
        # so we need to import all of the dock classes
        DockRegistry.load_all_docks()

        for dock in DockRegistry.docks:
            action = QtWidgets.QAction(dock.title, self)
            action.triggered.connect(lambda: self.add_new_frame(dock))
            viewMenu.addAction(action)

    def add_new_frame(self, docking_class):
        # create a new dock widget
        instance = docking_class()
        instance.showDock(self)


# The AppInterface ties everything together.
class AppInterface:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

        # Apply a modern dark-themed stylesheet.
        self.app.setStyleSheet(PathUtil.asset_file_contents("styles/gui.qss"))

        # Instantiate our MainWindow with integrated dockable frames.
        self.mainWin = MainWindow()
        self.mainWin.show()

    def tick(self):
        # Process events; useful if you have a larger system loop.
        self.app.processEvents()


# For standalone testing, run the application loop.
if __name__ == "__main__":
    interface = AppInterface()
    sys.exit(interface.app.exec_())
