from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel
from PyQt5.QtCore import Qt


# Helper function for applying styles using Qt Style Sheets.
def apply_style(
    widget, text_color=None, bg_color=None, font_size=None, extra_styles=""
):
    styles = []
    if text_color:
        styles.append(f"color: {text_color};")
    if bg_color:
        styles.append(f"background-color: {bg_color};")
    if font_size:
        styles.append(f"font-size: {font_size}px;")
    if extra_styles:
        styles.append(extra_styles)
    widget.setStyleSheet(" ".join(styles))


class LayoutUtility:
    def __init__(self, imdock):
        """
        Initialize with an ImmediateInspectorDock (or similar) instance.
        This builder does not cache widget pointers—every call creates new widgets.
        Persistent state for controls (like button clicks and toggles) is maintained.
        """
        self.dock = imdock
        # Use the dock's main layout as the starting point.
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

        # Persistent state dictionaries.
        self._button_state = {}  # Map: control label -> bool (one-shot click flag)
        self._toggle_state = {}  # Map: control label -> bool

    def button(
        self, label, text_color=None, bg_color=None, font_size=None, extra_styles=""
    ):
        """
        Creates a new button each time it is called.
        Returns True if the button was clicked (since the last rebuild), then resets the flag.
        """
        # Ensure persistent state exists.
        if label not in self._button_state:
            self._button_state[label] = False

        btn = QPushButton(label)
        apply_style(btn, text_color, bg_color, font_size, extra_styles)
        # When clicked, update the persistent state.
        btn.clicked.connect(lambda _, l=label: self._set_button_state(l, True))
        self._current_layout.addWidget(btn)

        # Read and then reset the one-shot flag.
        was_clicked = self._button_state[label]
        self._button_state[label] = False
        return was_clicked

    def _set_button_state(self, label, value):
        self._button_state[label] = value
        self.dock.set_dirty()

    def toggle(
        self,
        label,
        initial_value=False,
        text_color=None,
        bg_color=None,
        font_size=None,
        extra_styles="",
    ):
        """
        Creates a new toggle (checkbox) each time it is called.
        Returns the current boolean state.
        """
        # Use existing state if available.
        if label not in self._toggle_state:
            self._toggle_state[label] = initial_value

        chk = QCheckBox(label)
        chk.setChecked(self._toggle_state[label])
        apply_style(chk, text_color, bg_color, font_size, extra_styles)
        # When changed, update the persistent state.
        chk.stateChanged.connect(
            lambda state, l=label: self._set_toggle_state(l, state)
        )
        self._current_layout.addWidget(chk)
        return self._toggle_state[label]

    def _set_toggle_state(self, label, state):
        self._toggle_state[label] = state == Qt.Checked
        self.dock.set_dirty()

    def label(
        self, text, text_color=None, bg_color=None, font_size=None, extra_styles=""
    ):
        """
        Creates a new label each time it is called.
        """
        lbl = QLabel(text)
        apply_style(lbl, text_color, bg_color, font_size, extra_styles)
        self._current_layout.addWidget(lbl)
        return lbl

    def begin_horizontal(self):
        """
        Starts a horizontal grouping. Widgets added after this call will be arranged
        in a horizontal row until end_horizontal() is called.
        """
        h_layout = QHBoxLayout()
        self._current_layout.addLayout(h_layout)
        self._layout_stack.append(h_layout)
        self._current_layout = h_layout

    def end_horizontal(self):
        """
        Ends the current horizontal grouping.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_vertical(self):
        """
        Starts a vertical grouping.
        """
        v_layout = QVBoxLayout()
        self._current_layout.addLayout(v_layout)
        self._layout_stack.append(v_layout)
        self._current_layout = v_layout

    def end_vertical(self):
        """
        Ends the current vertical grouping.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def reset(self):
        """
        Resets one-shot states (e.g. button clicks).
        """
        for key in self._button_state:
            self._button_state[key] = False
