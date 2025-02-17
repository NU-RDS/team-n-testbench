from PyQt5.QtWidgets import QLabel
from interface.dock import dock, ImmediateInspectorDock

@dock("Dummy Dock")
class DummyDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)

    def draw_inspector(self):
        super().draw_inspector()
        print("Drawing inspector")

        # Use the builder API exclusively.
        self.builder.label(
            "This is a dummy dock widget",
            text_color="black",
            bg_color="lightgray",
            font_size=14
        )

        # Create a horizontal group with a button and toggle.
        self.builder.begin_horizontal()

        if self.builder.button("Test Button", text_color="white", bg_color="blue", font_size=12):
            print("Test Button was pressed!")

        toggle_val = self.builder.toggle("Enable Option", initial_value=True, text_color="black")
        self.builder.label(
            f"Option is {'ON' if toggle_val else 'OFF'}",
            text_color="green" if toggle_val else "red",
            font_size=12
        )
        
        self.builder.end_horizontal()

        # Create a vertical grouping with another label.
        self.builder.begin_vertical()
        self.builder.label(
            "This is a vertically grouped label",
            text_color="darkblue",
            font_size=16
        )
        self.builder.end_vertical()
