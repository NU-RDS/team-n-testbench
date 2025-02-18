import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QByteArray
import json

from util.path import PathUtil
from interface.dock import DockRegistry

from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robocom")
        self.setGeometry(100, 100, 800, 600)
        self.setDockNestingEnabled(True)
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)
        self.open_docks = {}  # key: dock instance name, value: dock instance
        
        self.setup_menus()
        # Load the workspace (docks + main window state)
        self.load_workspace()

    def setup_menus(self):
        menubar = self.menuBar()
        viewMenu = menubar.addMenu("View")

        DockRegistry.load_all_docks()
        for dock in DockRegistry.get_dock_names():
            docking_class = DockRegistry.get_dock(dock)
            action = viewMenu.addAction(dock)
            action.triggered.connect(lambda _, name=dock, cls=docking_class: self.add_new_frame(name, cls))

    def add_new_frame(self, docking_name, docking_class):
        # Create a new dock widget and give it a unique object name
        instance = docking_class()
        instance.show_dock(self)
        instance.setWindowTitle(docking_name)
        # Ensure unique object names for state restoration
        instance_name = f"{docking_name}_{len(self.open_docks)}"
        instance.setObjectName(f"{instance_name}")
        self.open_docks[instance_name] = instance

    def closeEvent(self, event):
        """Save workspace on close."""
        self.save_workspace()
        super().closeEvent(event)
        sys.exit(0)

    def save_workspace(self):
        """Save main window state, geometry, and open dock widgets."""
        print("Saving workspace...")
        try:
            window_state = self.saveState().toBase64().data().decode()
            geometry_state = self.saveGeometry().toBase64().data().decode()
            # Also save a list of open dock names
            open_dock_names = list(self.open_docks.keys())
            workspace = {
                "window_state": window_state,
                "geometry_state": geometry_state,
                "open_docks": open_dock_names,
            }
            with open(PathUtil.file("workspace.json"), "w") as file:
                json.dump(workspace, file, indent=2)
        except Exception as e:
            print(f"Error saving workspace: {e}")

    def load_workspace(self):
        """Load workspace and recreate docks before restoring window state."""
        if not PathUtil.file_exists("workspace.json"):
            return
        try:
            with open(PathUtil.file("workspace.json"), "r") as file:
                data = json.load(file)

            # Recreate the open docks
            open_dock_names = data.get("open_docks", [])
            for dock_name in open_dock_names:
                # get rid of the _# suffix
                # so anything before the last underscore is the dock name
                # and anything after is the instance number
                dock_name = dock_name.rsplit("_", 1)[0]               
                docking_class = DockRegistry.get_dock(dock_name)
                if docking_class:
                    self.add_new_frame(dock_name, docking_class)
                else:
                    print(f"Warning: No dock class found for {dock_name}")

            # Restore window state and geometry
            window_state = data.get("window_state", "")
            geometry_state = data.get("geometry_state", "")
            if window_state:
                self.restoreState(QByteArray.fromBase64(window_state.encode()))
            if geometry_state:
                self.restoreGeometry(QByteArray.fromBase64(geometry_state.encode()))
            print("Workspace loaded.")
        except Exception as e:
            print(f"Error loading workspace: {e}")

# The AppInterface ties everything together.
class AppInterface:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        # (Optional) apply a global stylesheet
        # from qt_material import apply_stylesheet
        apply_stylesheet(self.app, theme='light_purple.xml', invert_secondary=True)
        self.main_win = MainWindow()
        self.main_win.show()

    def tick(self):
        self.app.processEvents()

