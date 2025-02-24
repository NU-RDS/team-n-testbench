import pyqtgraph as pg
from PyQt5.QtCore import Qt
from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import FontStyle, LayoutAlignment
from app_context import ApplicationContext
from util.timer import TimerGroup, TimedTask

@dock("Telemetry Graph")
class TelemetryGraphDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a timer to refresh the graph periodically.
        self.timer_group.add_task(1000, self.redraw)
        # We'll create the plot widget once and update it on each draw.
        self.plot_widget = None

    def draw_inspector(self):
        # Begin new UI frame.
        self.builder.start()

        # If we haven't created the plot widget yet, create it.
        if self.plot_widget is None:
            self.plot_widget = pg.PlotWidget()
            # Set a dark background and white text to emulate a console/graph look.
            self.plot_widget.setBackground('k')
            self.plot_widget.showGrid(x=True, y=True)
            self.plot_widget.setLabel('left', 'Motor Position', color='w')
            self.plot_widget.setLabel('bottom', 'Time (s)', color='w')
            self.plot_widget.setTitle("Telemetry - Joint 1", color='w')
        else:
            # Reparent the plot widget into the current layout so it is visible.
            self.builder._current_layout.addWidget(self.plot_widget)

        # Retrieve telemetry data (for joint 1).
        telemetry = ApplicationContext.telemetry
        datastream = telemetry.get_datastream(1)
        if datastream is not None and len(datastream.snapshots) > 0:
            # Extract timestamps and motor positions.
            timestamps = [snapshot.timestamp for snapshot in datastream.snapshots]
            positions = [snapshot.motor_pos for snapshot in datastream.snapshots]
            # Update the plot.
            self.plot_widget.plot(timestamps, positions, clear=True, pen=pg.mkPen('w', width=2))
        else:
            # Clear the plot if no data.
            self.plot_widget.clear()

        # Optionally, add a flexible space below the plot.
        self.builder.flexible_space()

    def redraw(self):
        self.set_dirty()
        self.show()
