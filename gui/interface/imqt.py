from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLabel,
    QScrollArea,
    QWidget,
    QGroupBox,
    QSizePolicy,
    QSpacerItem,
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
        self._button_state = {}  # Map: unique widget ID -> bool (one-shot click flag)
        self._toggle_state = {}  # Map: unique widget ID -> bool
        self._foldout_state = {}  # Map: unique widget ID -> bool (expanded/collapsed)
        self._toggle_group_state = {}  # Map: unique widget ID -> bool (group enabled/disabled)

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

    # --------------------------------------------------------------------------
    # BUTTON
    # --------------------------------------------------------------------------
    def button(self, label, text_color=None, bg_color=None, font_size=None, extra_styles=""):
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

    # --------------------------------------------------------------------------
    # TOGGLE
    # --------------------------------------------------------------------------
    def toggle(self, label, initial_value=False, text_color=None, bg_color=None, font_size=None, extra_styles=""):
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
        self._toggle_state[widget_id] = state == Qt.Checked
        self.dock.set_dirty()
        self.dock.show()

    # --------------------------------------------------------------------------
    # LABEL
    # --------------------------------------------------------------------------
    def label(self, text, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        widget_id = self._get_key(text)
        lbl = QLabel(text)
        apply_style(lbl, text_color, bg_color, font_size, extra_styles)
        self._current_layout.addWidget(lbl)
        self.dock.set_dirty()
        return lbl

    # --------------------------------------------------------------------------
    # UTILITY
    # --------------------------------------------------------------------------
    def _compute_box_color(self):
        depth = len(self._layout_stack) - 1
        value = max(0, 220 - depth * 10)
        return f"rgb({value}, {value}, {value})"

    def _create_boxed_container(self, layout_class, indent=0, box_color=None):
        container = QWidget()
        # Create a unique object name for this container.
        unique_name = "boxedContainer_" + self._get_key("boxed")
        print(f"Unique name: {unique_name}")
        container.setObjectName(unique_name)
        layout = layout_class()
        layout.setContentsMargins(indent if indent else 0, 0, 0, 0)
        container.setLayout(layout)
        computed_color = box_color if box_color else self._compute_box_color()
        # Only apply border to the container, not its children.
        container.setStyleSheet(
            f"QWidget#{unique_name} {{ border: 1px solid {computed_color}; padding: 5px; }} "
            f"QWidget#{unique_name} * {{ border: none; }}"
        )
        return container, layout

    # --------------------------------------------------------------------------
    # GROUPING METHODS (WITH OPTIONAL BOXING AND INDENT)
    # --------------------------------------------------------------------------
    def begin_horizontal(self, boxed=False, box_color=None, indent=0):
        if boxed:
            container, layout = self._create_boxed_container(QHBoxLayout, indent, box_color)
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
            h_layout = QHBoxLayout()
            if indent:
                h_layout.setContentsMargins(indent, 0, 0, 0)
            self._current_layout.addLayout(h_layout)
            self._layout_stack.append(h_layout)
            self._current_layout = h_layout

    def end_horizontal(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_vertical(self, boxed=False, box_color=None, indent=0):
        if boxed:
            container, layout = self._create_boxed_container(QVBoxLayout, indent, box_color)
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
            v_layout = QVBoxLayout()
            if indent:
                v_layout.setContentsMargins(indent, 0, 0, 0)
            self._current_layout.addLayout(v_layout)
            self._layout_stack.append(v_layout)
            self._current_layout = v_layout

    def end_vertical(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # --------------------------------------------------------------------------
    # SCROLLABLE REGION
    # --------------------------------------------------------------------------
    def begin_scroll(self, orientation=Qt.Vertical):
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
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # --------------------------------------------------------------------------
    # FADE GROUP
    # --------------------------------------------------------------------------
    def begin_fade_group(self, initial_opacity=1.0):
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
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # --------------------------------------------------------------------------
    # FOLDOUT HEADER GROUP (STATEFUL) WITH INDENT OPTION USING PUSHBUTTON
    # --------------------------------------------------------------------------
    def begin_foldout_header_group(self, title, boxed=False, box_color=None, indent=10):
        widget_id = self._get_key(title)
        if widget_id not in self._foldout_state:
            self._foldout_state[widget_id] = True

        button = QPushButton()
        button.setCheckable(True)
        button.setChecked(self._foldout_state[widget_id])
        arrow = "v" if self._foldout_state[widget_id] else ">"
        button.setText(f"{arrow} {title}")
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setFixedHeight(20)
        button.setStyleSheet("QPushButton { text-align: left; padding: 2px 5px; margin: 0px; }")
        button.clicked.connect(lambda checked, wid=widget_id: self._on_foldout_toggled(checked, wid, title, button))
        self._current_layout.addWidget(button)

        if boxed:
            container, layout = self._create_boxed_container(QVBoxLayout, indent, box_color)
            self._layout_stack.append(layout)
            self._current_layout.addWidget(container)
            self._current_layout = layout
        else:
            v_layout = QVBoxLayout()
            v_layout.setContentsMargins(indent, 0, 0, 0)
            self._current_layout.addLayout(v_layout)
            self._layout_stack.append(v_layout)
            self._current_layout = v_layout

        return self._foldout_state[widget_id]

    def _on_foldout_toggled(self, checked, widget_id, title, button):
        self._set_foldout_state(widget_id, checked)
        new_arrow = "v" if checked else ">"
        button.setText(f"{new_arrow} {title}")

    def end_foldout_header_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def _set_foldout_state(self, widget_id, value):
        self._foldout_state[widget_id] = value
        self.dock.set_dirty()
        self.dock.show()

    # --------------------------------------------------------------------------
    # TOGGLE GROUP
    # --------------------------------------------------------------------------
    def begin_toggle_group(self, label, initial_state=True, boxed=False, box_color=None, indent=10):
        group_box = QGroupBox(label)
        group_box.setCheckable(True)
        group_box.setChecked(initial_state)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        if boxed:
            # Use a unique object name for the group box so the border applies only to it.
            unique_name = "boxedGroup_" + self._get_key("group")
            group_box.setObjectName(unique_name)
            computed_color = box_color if box_color else self._compute_box_color()
            group_box.setStyleSheet(
                f"QGroupBox#{unique_name} {{ border: 1px solid {computed_color}; padding: 5px; }} "
                f"QGroupBox#{unique_name} * {{ border: none; }}"
            )
        else:
            group_layout.setContentsMargins(indent, 0, 0, 0)
        self._current_layout.addWidget(group_box)
        self._layout_stack.append(group_layout)
        self._current_layout = group_layout
        return group_box

    def end_toggle_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # --------------------------------------------------------------------------
    # SPACE METHODS (Like Unity's GUILayout.Space and FlexibleSpace)
    # --------------------------------------------------------------------------
    def space(self, size=10):
        if isinstance(self._current_layout, QVBoxLayout):
            spacer = QSpacerItem(0, size, QSizePolicy.Fixed, QSizePolicy.Fixed)
        elif isinstance(self._current_layout, QHBoxLayout):
            spacer = QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            spacer = QSpacerItem(0, size, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._current_layout.addItem(spacer)

    def flexible_space(self):
        if isinstance(self._current_layout, QVBoxLayout):
            spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        elif isinstance(self._current_layout, QHBoxLayout):
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        else:
            spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self._current_layout.addItem(spacer)
