from PyQt5.QtWidgets import QLineEdit
from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle

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

    def draw_inspector(self):
        self.builder.start()
        print("Drawing console inspector")
        
        # Begin scrollable region for console output.
        self.builder.begin_scroll()
        for line in self.lines:
            print(f"Drawing line: {line}")
            self.builder.label(line, font_style=FontStyle.NORMAL)
        self.builder.end_scroll()

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
