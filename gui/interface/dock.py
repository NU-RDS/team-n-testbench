from PyQt5 import QtWidgets, QtOpenGL
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import pkgutil
import importlib
import interface.docks
from interface.imqt import LayoutUtility

class BaseDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        print("BaseDockWidget:__init__")
        # Allow the dock widget to be moved, floated, and closed.
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

    def show_dock(self, main_window, area=Qt.RightDockWidgetArea):
        """
        Instantiate the dock widget, add it to the provided main_window,
        and show it.
        """
        main_window.addDockWidget(area, self)
        self.show()


class ImmediateInspectorDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("Immediate Inspector", parent)
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
        # Initially mark the inspector as dirty so it builds its UI.
        self.is_dirty = True
                # Create a persistent LayoutUtility instance for this dock.
        self.builder = LayoutUtility(self)

    def show(self):
        """
        Rebuild the inspector UI if it is marked as dirty.
        This simulates an immediate-mode GUI where the UI is regenerated when needed.
        """
        print("Showing Immediate Inspector dock")
        if not self.is_dirty:
            # No update needed if not dirty.
            super().show()  # Still show the dock
            return

        # Clear the current layout.
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        print("Rebuilding inspector UI...")
        self.draw_inspector()
        self.is_dirty = False
        super().show()

    def set_dirty(self):
        """
        Mark the inspector as dirty so that its UI will be rebuilt.
        """
        self.is_dirty = True

    def draw_inspector(self):
        """
        Rebuild the inspector UI.
        Override this method in your dock subclasses to provide custom content.
        For demonstration, we simply add a label.
        """
        pass


def dock(name):
    """
    A decorator that adds a dock widget to the DockRegistery.
    """

    def decorator(cls):
        DockRegistry.add_dock(name, cls)
        return cls

    return decorator


class DockRegistry:
    docks = {}  # global to hold all dock widgets by name

    @staticmethod
    def add_dock(name, cls):
        print(f"Adding dock: {name}")
        DockRegistry.docks[name] = cls

    @staticmethod
    def get_dock(name):
        return DockRegistry.docks.get(name)

    @staticmethod
    def get_dock_names():
        return DockRegistry.docks.keys()

    @staticmethod
    def load_all_docks():
        """
        Dynamically imports all modules in the interface.docks package.
        This will cause each dock class (decorated with @dock) to register itself.
        """
        package = interface.docks
        for finder, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package.__name__}.{module_name}"
            importlib.import_module(full_module_name)
