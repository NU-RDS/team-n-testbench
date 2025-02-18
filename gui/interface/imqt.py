from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLabel,
    QScrollArea,
    QWidget,
    QToolButton,
    QGroupBox,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect

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

    # -------------------------------------------------------------------------
    # GROUPING
    # -------------------------------------------------------------------------
    def begin_horizontal(self):
        h_layout = QHBoxLayout()
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self._current_layout.addLayout(h_layout)
        self._layout_stack.append(h_layout)
        self._current_layout = h_layout

    def end_horizontal(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_vertical(self):
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        self._current_layout.addLayout(v_layout)
        self._layout_stack.append(v_layout)
        self._current_layout = v_layout

    def end_vertical(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # -------------------------------------------------------------------------
    # SCROLLING
    # -------------------------------------------------------------------------
    def begin_scroll(self, orientation=Qt.Vertical):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        if orientation == Qt.Vertical:
            container_layout = QVBoxLayout()
        else:
            container_layout = QHBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        scroll_area.setWidget(container)
        self._current_layout.addWidget(scroll_area)
        self._layout_stack.append(container_layout)
        self._current_layout = container_layout

    def end_scroll(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # -------------------------------------------------------------------------
    # FADE GROUP
    # -------------------------------------------------------------------------
    def begin_fade_group(self, initial_opacity=1.0):
        container = QWidget()
        effect = QGraphicsOpacityEffect(container)
        effect.setOpacity(initial_opacity)
        container.setGraphicsEffect(effect)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        self._current_layout.addWidget(container)
        self._layout_stack.append(container_layout)
        self._current_layout = container_layout
        return effect

    def end_fade_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # -------------------------------------------------------------------------
    # FOLDOUT HEADER GROUP
    # -------------------------------------------------------------------------
    def begin_foldout_header_group(self, title):
        """
        Begins a foldout header group that spans the full width,
        with minimal margins and spacing, to look slimmer.
        """
        # Container for the entire foldout group
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create a toggle button that acts as the header
        header_button = QToolButton()
        header_button.setText(title)
        header_button.setCheckable(True)
        header_button.setChecked(True)
        header_button.setArrowType(Qt.DownArrow)

        # Force the button to expand horizontally, but keep it short vertically
        header_button.setSizePolicy(
            QSizePolicy.Expanding, 
            QSizePolicy.Fixed
        )
        header_button.setFixedHeight(24)  # <= Adjust for a slimmer height
        # Minimal padding in the button
        header_button.setStyleSheet("QToolButton { text-align: left; padding: 2px; }")

        # Container for the foldout's content
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(6, 2, 6, 2)

        # Show/hide content container
        def toggle_content(checked):
            content_container.setVisible(checked)
            header_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        header_button.toggled.connect(toggle_content)

        container_layout.addWidget(header_button)
        container_layout.addWidget(content_container)

        # Add the entire container to the current layout
        self._current_layout.addWidget(container)

        # Now push the content's layout onto the stack
        self._layout_stack.append(content_layout)
        self._current_layout = content_layout

        return header_button

    def end_foldout_header_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # -------------------------------------------------------------------------
    # TOGGLE GROUP
    # -------------------------------------------------------------------------
    def begin_toggle_group(self, label, initial_state=True):
        group_box = QGroupBox(label)
        group_box.setCheckable(True)
        group_box.setChecked(initial_state)

        # Minimal spacing to keep it tight
        group_layout = QVBoxLayout()
        group_layout.setSpacing(0)
        group_layout.setContentsMargins(6, 2, 6, 2)

        group_box.setLayout(group_layout)
        self._current_layout.addWidget(group_box)
        self._layout_stack.append(group_layout)
        self._current_layout = group_layout
        return group_box

    def end_toggle_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]
