from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLabel
)
from PyQt5.QtCore import Qt

def apply_style(widget, text_color=None, bg_color=None, font_size=None, extra_styles=""):
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
        This builder does not cache widget pointers—each call creates new widgets.
        Persistent state (for buttons, toggles, etc.) is maintained using unique keys.
        """
        self.dock = imdock
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

        # Persistent state dictionaries.
        self._button_state = {}   # Map: unique widget ID -> bool (one-shot click flag)
        self._toggle_state = {}   # Map: unique widget ID -> bool

        # Counter dictionary for generating unique keys.
        self._key_counter = {}

    def start(self):
        """
        Resets the key counters. Call this at the beginning of each inspector update.
        """
        self._key_counter = {}
        # Reset the layout stack to start with the main layout.
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

    def _get_key(self, base_key):
        """
        Utility function that generates a unique widget ID based on the base_key.
        For the first occurrence it returns base_key, then appends a number for subsequent ones.
        """
        if base_key not in self._key_counter:
            self._key_counter[base_key] = 0
            return base_key
        else:
            self._key_counter[base_key] += 1
            return f"{base_key} {self._key_counter[base_key]}"

    def button(self, label, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        """
        Creates a new button each time.
        Returns True if the button was clicked (since the last call) then resets the flag.
        """
        widget_id = self._get_key(label)
        if widget_id not in self._button_state:
            self._button_state[widget_id] = False

        btn = QPushButton(label)
        apply_style(btn, text_color, bg_color, font_size, extra_styles)
        btn.clicked.connect(lambda _, wid=widget_id: self._set_button_state(wid, True))
        self._current_layout.addWidget(btn)
        self.dock.set_dirty()
        was_clicked = self._button_state[widget_id]
        self._button_state[widget_id] = False  # Reset one-shot flag
        return was_clicked

    def _set_button_state(self, widget_id, value):
        self._button_state[widget_id] = value
        self.dock.set_dirty()
        self.dock.show()

    def toggle(self, label, initial_value=False, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        """
        Creates a new toggle (checkbox) each time.
        Returns the current boolean state.
        """
        widget_id = self._get_key(label)
        if widget_id not in self._toggle_state:
            self._toggle_state[widget_id] = initial_value

        chk = QCheckBox(label)
        chk.setChecked(self._toggle_state[widget_id])
        apply_style(chk, text_color, bg_color, font_size, extra_styles)
        chk.stateChanged.connect(lambda state, wid=widget_id: self._set_toggle_state(wid, state))
        self._current_layout.addWidget(chk)
        self.dock.set_dirty()
        return self._toggle_state[widget_id]

    def _set_toggle_state(self, widget_id, state):
        print(f"Setting toggle state: {widget_id} -> {state}")
        self._toggle_state[widget_id] = (state == Qt.Checked)
        self.dock.set_dirty()
        self.dock.show()

    def label(self, text, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        """
        Creates a new label each time.
        """
        widget_id = self._get_key(text)
        lbl = QLabel(text)
        apply_style(lbl, text_color, bg_color, font_size, extra_styles)
        self._current_layout.addWidget(lbl)
        self.dock.set_dirty()
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

