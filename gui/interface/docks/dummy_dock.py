from PyQt5.QtWidgets import QLabel

from interface.dock import (
    dock,
    ImmediateInspectorDock
)

@dock("Immediate Inspector")
class DummyDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_dirty()

    def draw_inspector(self):
        super().draw_inspector()
        print("Drawing inspector")
        self.layout.addWidget(QLabel("This is a dummy dock widget"))
        self.layout.addWidget(QLabel("It's a placeholder for the real thing"))
        self.layout.addWidget(QLabel("You can add your own widgets here"))
        self.layout.addWidget(QLabel("Or remove this and add your own custom dock"))
        self.layout.addWidget(QLabel("It's up to you!"))
        self.set_dirty()