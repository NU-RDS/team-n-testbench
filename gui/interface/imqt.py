from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLabel,
    QScrollArea,
    QWidget,
    QToolButton,
    QGroupBox
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

    def _compute_box_color(self):
        """
        Computes a border color based on the current depth.
        """
        depth = len(self._layout_stack) - 1
        value = max(0, 220 - depth * 10)
        return f"rgb({value}, {value}, {value})"

    # --- Grouping methods with optional boxing ---

    def begin_horizontal(self, boxed=False, box_color=None):
        """
        Begins a horizontal grouping.
        If boxed is True, wraps the group in a container with a border.
        """
        if boxed:
            container = QWidget()
            layout = QHBoxLayout()
            container.setLayout(layout)
            computed_color = box_color if box_color else self._compute_box_color()
            container.setStyleSheet(f"border: 1px solid {computed_color}; padding: 5px;")
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
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

    def begin_vertical(self, boxed=False, box_color=None):
        """
        Begins a vertical grouping.
        If boxed is True, wraps the group in a container with a border.
        """
        if boxed:
            container = QWidget()
            layout = QVBoxLayout()
            container.setLayout(layout)
            computed_color = box_color if box_color else self._compute_box_color()
            container.setStyleSheet(f"border: 1px solid {computed_color}; padding: 5px;")
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
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

    def begin_scroll(self, orientation=Qt.Vertical):
        """
        Begins a scrollable region.
        Widgets added after this call will be placed inside a scrollable container.
        
        :param orientation: Qt.Vertical (default) for vertical scrolling,
                            or Qt.Horizontal for horizontal scrolling.
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        if orientation == Qt.Vertical:
            container_layout = QVBoxLayout()
        else:
            container_layout = QHBoxLayout()
        container.setLayout(container_layout)
        scroll_area.setWidget(container)
        self._current_layout.addWidget(scroll_area)
        self._layout_stack.append(container_layout)
        self._current_layout = container_layout

    def end_scroll(self):
        """
        Ends the current scrollable region.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_fade_group(self, initial_opacity=1.0):
        """
        Begins a fade group.
        Creates a container with a QGraphicsOpacityEffect so its opacity (and visibility)
        can be controlled or animated.
        
        :param initial_opacity: Float between 0.0 (fully transparent) and 1.0 (fully opaque).
        :return: The QGraphicsOpacityEffect for further adjustments.
        """
        container = QWidget()
        effect = QGraphicsOpacityEffect(container)
        effect.setOpacity(initial_opacity)
        container.setGraphicsEffect(effect)
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        self._current_layout.addWidget(container)
        self._layout_stack.append(container_layout)
        self._current_layout = container_layout
        return effect

    def end_fade_group(self):
        """
        Ends the current fade group.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_foldout_header_group(self, title, boxed=False, box_color=None):
        """
        Begins a foldout header group that spans the full width.
        The header is implemented as a toggle button with special styling.
        
        :param title: The header title.
        :param boxed: If True, wraps the foldout in a box.
        :param box_color: Optional border color for the box.
        :return: The QToolButton used as the foldout header.
        """
        # Create a container for the entire foldout group.
        container = QWidget()
        if boxed:
            computed_color = box_color if box_color else self._compute_box_color()
            container.setStyleSheet(f"border: 1px solid {computed_color}; padding: 5px;")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)

        # Create a toggle button that acts as the header.
        header_button = QToolButton()
        header_button.setText(title)
        header_button.setCheckable(True)
        header_button.setChecked(True)
        header_button.setArrowType(Qt.DownArrow)
        # Force the button to expand to full width.
        header_button.setSizePolicy(header_button.sizePolicy().Expanding, header_button.sizePolicy().Preferred)
        header_button.setStyleSheet("text-align: left; padding: 5px;")
        
        # Create a container for the foldout's content.
        content_container = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_container.setLayout(content_layout)
        
        # When the header is toggled, show/hide the content container.
        def toggle_content(checked):
            content_container.setVisible(checked)
            header_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        header_button.toggled.connect(toggle_content)
        
        container_layout.addWidget(header_button)
        container_layout.addWidget(content_container)
        self._current_layout.addWidget(container)
        # Push the content layout onto the stack so subsequent widgets are added there.
        self._layout_stack.append(content_layout)
        self._current_layout = content_layout
        return header_button

    def end_foldout_header_group(self):
        """
        Ends the current foldout header group.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_toggle_group(self, label, initial_state=True, boxed=False, box_color=None):
        """
        Begins a toggle group.
        Creates a vertical group wrapped in a checkable QGroupBox.
        
        :param label: The label to display in the group header.
        :param initial_state: Whether the group is initially enabled.
        :param boxed: If True, apply a border to the group.
        :param box_color: Optional border color.
        :return: The QGroupBox created.
        """
        group_box = QGroupBox(label)
        group_box.setCheckable(True)
        group_box.setChecked(initial_state)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        if boxed:
            computed_color = box_color if box_color else self._compute_box_color()
            group_box.setStyleSheet(f"border: 1px solid {computed_color}; padding: 5px;")
        self._current_layout.addWidget(group_box)
        self._layout_stack.append(group_layout)
        self._current_layout = group_layout
        return group_box

    def end_toggle_group(self):
        """
        Ends the current toggle group.
        """
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]
