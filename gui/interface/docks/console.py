from PyQt5.QtWidgets import QLineEdit
from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle
from PyQt5.QtCore import Qt

@dock("Console")
class ConsoleDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []  # list of console output lines
        self.command_input_field = None  # persistent QLineEdit for command input
        self.force_input_focus = True  # flag to force focus on the input field

    def add_line(self, line):
        """Append a new line to the console output and mark for redraw."""
        self.lines.append(line)
        self.set_dirty()

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

    def draw_console(self):
        # draw the console UI
        # so we combine all of the lien into a single string with \n as separator
        console_text = "\n".join(self.lines)

        # Begin scrollable region for console output.
        self.builder.begin_scroll()

        styles = [
            "font-family: 'Courier New', monospace;",  # Monospaced font.
            "font-size: 12px;",                        # Reasonable font size.
            "padding: 10px;",                          # Some internal padding.
            "border: 1px solid #333;",                 # A dark border.
            "white-space: pre-wrap;"                   # Preserve line breaks
        ]
        # and we draw the label with a slightly darker background color, make it transparent
        label = self.builder.label(console_text, bg_color="rgba(0, 0, 0, 0.1)", extra_styles=styles)
        label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.builder.end_scroll()

    def draw_inspector(self):
        self.builder.start()
        print("Drawing console inspector")
    
        # Draw the console output.
        self.draw_console()

        # Horizontal grouping for input controls.
        self.builder.begin_horizontal()

        # Add a "Clear" button to clear the console.
        if self.builder.button("Clear"):
            self.lines.clear()

        # Create the command input field once if it doesn't exist.
        if self.command_input_field is None:
            self.command_input_field = QLineEdit()
            self.command_input_field.setPlaceholderText("Enter command here...")
            self.command_input_field.returnPressed.connect(self.process_command)

        # Manually add the QLineEdit widget into the current layout.
        self.builder._current_layout.addWidget(self.command_input_field)
        self.builder.end_horizontal()

        # If the force flag is set, reassign focus to the input field.
        if self.force_input_focus and self.command_input_field is not None:
            self.command_input_field.setFocus()
