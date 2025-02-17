from PyQt5.QtWidgets import QVBoxLayout, QPushButton


class LayoutUtility:
    def __init__(self, imdock):
        """
        Initialize the builder with a parent widget. If the parent
        does not already have a layout, a QVBoxLayout is created.
        """
        self.dock = imdock
        # These dictionaries hold persistent button widgets and their click state.
        self._instance_buttons = {} # Map : button label -> QPushButton
        self._state_button = {}  # Map: button label -> bool

    def button(self, label):
        """
        Create (or retrieve) a persistent button with the given label.
        Returns True if the button was clicked since the last check,
        and resets the click state.
        """
        # Create the button only once.
        btn = None
        if self._instance_buttons.get(label) is None:
            btn = QPushButton(label)
            # Connect the clicked signal to update our state.
            btn.clicked.connect(lambda _, l=label: self._on_button_clicked(l))
        else:
            btn = self._instance_buttons[label]
            
        self.dock.layout.addWidget(btn)
        if self._state_button.get(label) is None:
            self._state_button[label] = False
        self.dock.set_dirty()

        was_clicked = self._state_button[label]
        self._state_button[label] = False
        return was_clicked

    def _on_button_clicked(self, label):
        print("Button clicked!")
        self._state_button[label] = True
        self.dock.set_dirty()
        self.dock.show()

    def reset(self):
        """
        Reset all button click states. You can call this at the beginning
        of your UI update (or “frame”) if needed.
        """
        for key in self._state_button:
            self._state_button[key] = False
