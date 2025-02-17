from PyQt5 import QtWidgets, QtOpenGL
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class BaseDockWidget(QDockWidget):
    @classmethod
    def showDock(cls, main_window, area=Qt.DockWidgetArea.RightDockWidgetArea):
        """
        Instantiate the dock widget, add it to the provided main_window,
        and show it.
        """
        instance = cls(main_window)
        main_window.addDockWidget(area, instance)
        instance.show()
        return instance

class ImmediateInspectorDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("Immediate Inspector", parent)
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
        self.is_dirty = False


    def drawInspector(self):
        """
        Rebuilds the inspector UI. In a true immediate mode system, you'd
        re-run your UI code each frame. Here we clear and rebuild the layout.
        """
        if self.is_dirty:
            return

        # Clear the current layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.drawInspector()
        self.is_dirty = False

    def set_dirty(self):
        """
        This is a dummy method to simulate a change in state that would
        require a UI update.
        """
        self.is_dirty = True

    @classmethod
    def drawInspector(self):
        """
        Rebuilds the inspector UI.
        """

def dock(name):
    """
    A decorator that adds a dock widget to the DockRegistery.
    """
    def decorator(cls):
        DockRegistry.addDock(name, cls)
        return cls
    return decorator

class DockRegistry:
    docks = {} # global to hold all dock widgets by name

    @staticmethod
    def addDock(name, cls):
        DockRegistry.docks[name] = cls

    @staticmethod
    def getDock(name):
        return DockRegistry.docks.get(name)
    
    @staticmethod
    def getDockNames():
        return DockRegistry.docks.keys()