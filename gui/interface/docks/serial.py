from PyQt5.QtWidgets import QLineEdit
from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle
from PyQt5.QtCore import Qt
from app_context import ApplicationContext

@dock("Serial")
class SerialDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)

    def process_command(self):
        """Called when the user presses Enter in the input field."""
        command = self.command_input_field.text().strip()
        print(f"Processing command: {command}")
        if command:
            # For demonstration, simply echo the command
            self.add_line(f"> {command}")
            # Here you could also call a command interpreter
        self.command_input_field.clear()
        self.set_dirty()
        self.show()

    def draw_serial(self):
        # draw the console UI
        # so we combine all of the lien into a single string with \n as separator
        history_raw = ApplicationContext.mcu_com.channel.get_history()
        # turn this into a string
        history = history_raw.decode("utf-8")

        # Begin scrollable region for console output.
        self.builder.begin_scroll()
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

    def draw_inspector(self):
        self.builder.start()    
        # Draw the console output.
        self.draw_serial()

        # Add a "Clear" button to clear the console.
        if self.builder.button("Clear"):
            ApplicationContext.mcu_com.channel.clear_history()
            self.set_dirty()
            self.show()
