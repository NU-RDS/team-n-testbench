from PyQt5.QtWidgets import QLineEdit
from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle
from PyQt5.QtCore import Qt
from app_context import ApplicationContext

@dock("Serial")
class SerialDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer_group.add_task(2000, self.redraw)


    def draw_serial(self):
        # draw the console UI
        # so we combine all of the lien into a single string with \n as separator
        history = ApplicationContext.mcu_com.channel.get_history()

        # Begin scrollable region for console output.
        self.builder.begin_scroll(keep_bottom=True)
        styles = [
            "font-family: 'Courier New', monospace;",  # Monospaced font.
            "font-size: 12px;",                        # Reasonable font size.
            "padding: 10px;",                          # Some internal padding.
            "border: 1px solid #333;",                 # A dark border.
            "white-space: pre-wrap;"                   # Preserve line breaks.
        ]
        # and we draw the label with a slightly darker background color, make it transparent
        label = self.builder.label(history, bg_color="rgba(0, 0, 0, 0.1)", extra_styles=styles)
        label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.builder.end_scroll()

    def redraw(self):
        self.set_dirty()
        self.show()

    def draw_inspector(self):
        self.builder.start()    
        # Draw the console output.
        self.draw_serial()

        self.builder.begin_horizontal()
        if self.builder.button("Clear"):
            ApplicationContext.mcu_com.channel.clear_history()
            self.set_dirty()
            self.show()
        
        self.builder.end_horizontal()
