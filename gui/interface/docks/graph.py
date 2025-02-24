import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from interface.dock import BaseDockWidget, dock
from app_context import ApplicationContext

class GraphUpdateWorker(QThread):
    # Emit two lists: one for joint 1 and one for joint 2. Each is a 2-element list:
    # [timestamps, motor_positions].
    data_ready = pyqtSignal(list, list)

    def __init__(self, telemetry, parent=None):
        super().__init__(parent)
        self.telemetry = telemetry
        self.running = True

    def run(self):
        while self.running:
            # Retrieve datastreams for joint 1 and joint 2.
            ds1 = self.telemetry.get_datastream(1)
            ds2 = self.telemetry.get_datastream(2)
            timestamps1, positions1 = [], []
            timestamps2, positions2 = [], []
            if ds1 is not None and ds1.snapshots:
                for snap in ds1.snapshots:
                    timestamps1.append(snap.timestamp)
                    positions1.append(snap.motor_pos)
            if ds2 is not None and ds2.snapshots:
                for snap in ds2.snapshots:
                    timestamps2.append(snap.timestamp)
                    positions2.append(snap.motor_pos)
            self.data_ready.emit([timestamps1, positions1], [timestamps2, positions2])
            self.msleep(100)  # Update every 100 ms

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

@dock("Telemetry Graph")
class TelemetryGraphDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("Telemetry Graph", parent)
        self.setWindowTitle("Telemetry Graph")
        # Create a persistent main widget with a vertical layout.
        self.main_widget = QWidget(self)
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        # Create a persistent PlotWidget.
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Motor Position', color='w')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='w')
        self.layout.addWidget(self.plot_widget)
        # Create and start the worker thread for telemetry updates.
        self.worker = GraphUpdateWorker(ApplicationContext.telemetry)
        self.worker.data_ready.connect(self.update_graph)
        self.worker.start()

    def update_graph(self, data1, data2):
        """
        data1 and data2 are each lists of [timestamps, motor_positions].
        Plot joint1's data in white and joint2's data in red.
        """
        self.plot_widget.clear()
        if data1[0] and data1[1]:
            self.plot_widget.plot(data1[0], data1[1], pen=pg.mkPen('w', width=2))
        if data2[0] and data2[1]:
            self.plot_widget.plot(data2[0], data2[1], pen=pg.mkPen('r', width=2))

    def closeEvent(self, event):
        # Stop the worker thread when the dock is closed.
        self.worker.stop()
        super().closeEvent(event)
