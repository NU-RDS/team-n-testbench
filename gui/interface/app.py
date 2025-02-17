import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QSettings

from util.path import PathUtil
from interface.dock import DockRegistry



# Our main window contains the central OpenGL widget and several dockable frames.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Tendon Robotic Finger Control GUI")
        self.setGeometry(100, 100, 800, 600)
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
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        # Save list of open docks (by their object names)
        open_dock_names = list(self.open_docks.keys())
        settings.setValue("openDocks", open_dock_names)
        print("Workspace saved:", open_dock_names)

    def load_workspace(self):
        """
        Load the main window geometry, state, and re-create any open dock widgets.
        """
        settings = QSettings("MyCompany", "MyApp")
        geometry = settings.value("geometry")
        state = settings.value("windowState")
        open_dock_names = settings.value("openDocks", [])
        if open_dock_names:
            print("Restoring docks:", open_dock_names)
            # Re-create the dock widgets based on the saved names.
            for dock_name in open_dock_names:
                docking_class = DockRegistry.get_dock(dock_name)
                if docking_class is not None:
                    self.add_new_frame(dock_name, docking_class)
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)


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
