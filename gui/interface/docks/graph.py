import pyqtgraph as pg
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from interface.dock import BaseDockWidget, dock
from app_context import ApplicationContext
import time

class GraphUpdateWorker(QThread):
    # Emit two sets of data: one for joint 1 and one for joint 2.
    # Each is a tuple: (timestamps, motor_positions)
    data_ready = pyqtSignal(tuple, tuple)
    
    def __init__(self, telemetry, update_interval=200, parent=None):
        super().__init__(parent)
        self.telemetry = telemetry
        self.update_interval = update_interval  # in milliseconds
        self.running = True

    def run(self):
        while self.running:
            # Retrieve telemetry data for joint 1 and joint 2.
            ds1 = self.telemetry.get_datastream(0)
            ds2 = self.telemetry.get_datastream(1)
            
            t1, p1 = [], []
            t2, p2 = [], []
            if ds1 is not None and ds1.snapshots:
                for snap in ds1.snapshots:
                    t1.append(snap.timestamp)
                    p1.append(snap.motor_pos)
            if ds2 is not None and ds2.snapshots:
                for snap in ds2.snapshots:
                    t2.append(snap.timestamp)
                    p2.append(snap.motor_pos)
            
            self.data_ready.emit((t1, p1), (t2, p2))
            self.msleep(self.update_interval)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait()

@dock("Telemetry Graph")
class TelemetryGraphDock(BaseDockWidget):
    def __init__(self, parent=None):
        super().__init__("Telemetry Graph", parent)
        self.setWindowTitle("Telemetry Graph")
        
        # Create persistent main widget and layout.
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
        
        # Create persistent curves for joint 1 and joint 2.
        self.curve1 = self.plot_widget.plot([], [], pen=pg.mkPen('w', width=2))
        self.curve2 = self.plot_widget.plot([], [], pen=pg.mkPen('r', width=2))
        
        # Start a worker thread to update the graph.
        self.worker = GraphUpdateWorker(ApplicationContext.telemetry, update_interval=200)
        self.worker.data_ready.connect(self.update_graph)
        self.worker.start()
        
    def update_graph(self, data1, data2):
        """
        data1 and data2 are tuples: (timestamps, motor_positions).
        """
        if data1[0] and data1[1]:
            self.curve1.setData(data1[0], data1[1])
        if data2[0] and data2[1]:
            self.curve2.setData(data2[0], data2[1])
        
    def closeEvent(self, event):
        # Stop the worker thread when closing.
        self.worker.stop()
        super().closeEvent(event)
