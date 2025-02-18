import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QSettings, Qt, QByteArray

from util.path import PathUtil
from interface.dock import DockRegistry
import json

from qt_material import apply_stylesheet


# Our main window contains the central OpenGL widget and several dockable frames.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robocom")
        self.setGeometry(100, 100, 800, 600)
        self.setDockNestingEnabled(True)
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)
        self.open_docks = {}  # Keep track of open dock widgets
        # Create a menu to add new frames dynamically.
        self.setup_menus()
        self.load_workspace()

    def setup_menus(self):
        menubar = self.menuBar()
        viewMenu = menubar.addMenu("View")

        # find all of the dock classes and add them to the menu
        # so we need to import all of the dock classes
        DockRegistry.load_all_docks()

        for dock in DockRegistry.get_dock_names():
            docking_class = DockRegistry.get_dock(dock)
            # add a view menu item for each dock
            action = viewMenu.addAction(dock)
            # connect the action to a lambda that creates a new frame
            action.triggered.connect(lambda _, name=dock, cls=docking_class: self.add_new_frame(name, cls))

    def add_new_frame(self, docking_name, docking_class):
        # create a new dock widget
        instance = docking_class()
        instance.show_dock(self)
        # set the title of the dock widget
        instance.setWindowTitle(docking_name)
        # store the dock widget so we can save it later
        self.open_docks[docking_name] = instance
    


    def closeEvent(self, event):
        """
        Overriding closeEvent to save the workspace before exiting.
        """
        self.save_workspace()
        super().closeEvent(event)
        exit()


    def save_workspace(self):
        """
        Save the main window geometry, state, and list of open dock names.
        """
        print("Saving workspace...")
        docks = []
        for dock_name, dock_widget in self.open_docks.items():
            dock_geometry = dock_widget.saveGeometry()
            geometry_bytes = bytes(dock_geometry.toHex()).decode("ascii")
            docks.append({"dock": dock_name, "geometry": geometry_bytes})

        with open(PathUtil.file("workspace.json"), "w") as file:
            json.dump(docks, file, indent=4)

        

    def load_workspace(self):
        """
        Load the main window geometry, state, and re-create any open dock widgets.
        """
        if not PathUtil.file_exists("workspace.json"):
            return
        try:
            with open(PathUtil.file("workspace.json"), "r") as file:
                docks = json.load(file)
                for dock in docks:
                    dock_name = dock["dock"]
                    dock_geometry = QByteArray.fromHex(bytes(dock["geometry"], "ascii"))
                    docking_class = DockRegistry.get_dock(dock_name)
                    instance = docking_class()
                    instance.restoreGeometry(dock_geometry)
                    instance.show_dock(self)
                    self.open_docks[dock_name] = instance
        except Exception as e:
            print(f"Error loading workspace: {e}")
            return
            
        


# The AppInterface ties everything together.
class AppInterface:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        
        apply_stylesheet(self.app, theme='light_purple.xml', invert_secondary=True)
        # Instantiate our MainWindow with integrated dockable frames.
        self.main_win = MainWindow()
        self.main_win.show()

    def tick(self):
        # Process events; useful if you have a larger system loop.
        self.app.processEvents()


# For standalone testing, run the application loop.
if __name__ == "__main__":
    interface = AppInterface()
    sys.exit(interface.app.exec_())
