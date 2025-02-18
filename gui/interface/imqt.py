from enum import Enum
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
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class FontStyle(Enum):
    NORMAL = 0
    BOLD = 1
    ITALIC = 2
    BOLD_ITALIC = 3


def apply_style(
    widget,
    text_color=None,
    bg_color=None,
    font_size=None,
    extra_styles="",
    font_style=FontStyle.NORMAL
):
    """
    Applies the given style options to 'widget'.
    Now supports bold, italic, or bold+italic via 'font_style'.
    """
    styles = []

    # text color
    if text_color:
        styles.append(f"color: {text_color};")

    # background color
    if bg_color:
        styles.append(f"background-color: {bg_color};")

    # font size
    if font_size:
        styles.append(f"font-size: {font_size}px;")

    # font style
    if font_style in (FontStyle.BOLD, FontStyle.BOLD_ITALIC):
        styles.append("font-weight: bold;")
    if font_style in (FontStyle.ITALIC, FontStyle.BOLD_ITALIC):
        styles.append("font-style: italic;")

    # any extra CSS
    if extra_styles:
        # if this is just a string, append it as-is
        if isinstance(extra_styles, str):
            styles.append(extra_styles)
        # if it's a list, join the items with a space
        elif isinstance(extra_styles, list):
            styles.append(" ".join(extra_styles))

    widget.setStyleSheet(" ".join(styles))


class LayoutUtility:
    def __init__(self, imdock):
        """
        Initialize with an ImmediateInspectorDock (or similar) instance.
        """
        self.dock = imdock
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

        # Persistent state dictionaries.
        self._button_state = {}
        self._toggle_state = {}
        self._foldout_state = {}
        self._toggle_group_state = {}

        # Counter dictionary for generating unique keys.
        self._key_counter = {}

    def start(self):
        """Resets the key counters at the beginning of each inspector update."""
        self._key_counter = {}
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

    def _get_key(self, base_key):
        """
        Generates a unique widget ID based on base_key.
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
        self._button_state[widget_id] = False
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
        self._toggle_state[widget_id] = (state == Qt.Checked)
        self.dock.set_dirty()
        self.dock.show()

    # --------------------------------------------------------------------------
    # LABEL (with optional FontStyle)
    # --------------------------------------------------------------------------
    def label(
        self,
        text,
        text_color=None,
        bg_color=None,
        font_size=None,
        extra_styles="",
        font_style=FontStyle.NORMAL
    ):
        """
        Creates a new label each time. You can specify font_style as:
        FontStyle.NORMAL, FontStyle.BOLD, FontStyle.ITALIC, or FontStyle.BOLD_ITALIC
        """
        widget_id = self._get_key(text)
        lbl = QLabel(text)
        # Pass 'font_style' into apply_style
        apply_style(lbl, text_color, bg_color, font_size, extra_styles, font_style=font_style)
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
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(1)

        frame_id = self._get_key("box")
        computed_color = box_color if box_color else self._compute_box_color()
        frame.setObjectName(frame_id)
        # Only the QFrame gets the border, children are unaffected
        frame.setStyleSheet(f"QFrame#{frame_id} {{ border: 1px solid {computed_color}; padding: 5px; }}")

        layout = layout_class()
        layout.setContentsMargins(indent, 0, 0, 0)
        frame.setLayout(layout)
        return frame, layout

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
    # FOLDOUT HEADER GROUP (STATEFUL) USING PUSHBUTTON
    # --------------------------------------------------------------------------
    def begin_foldout_header_group(self, title, boxed=False, box_color=None, indent=0):
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

        def _on_foldout_toggled(checked, wid=widget_id):
            self._set_foldout_state(wid, checked)
            new_arrow = "v" if checked else ">"
            button.setText(f"{new_arrow} {title}")

        button.clicked.connect(lambda checked, wid=widget_id: _on_foldout_toggled(checked, wid))
        self._current_layout.addWidget(button)

        if boxed:
            container, layout = self._create_boxed_container(QVBoxLayout, indent, box_color)
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
            v_layout = QVBoxLayout()
            v_layout.setContentsMargins(indent, 0, 0, 0)
            self._current_layout.addLayout(v_layout)
            self._layout_stack.append(v_layout)
            self._current_layout = v_layout

        return self._foldout_state[widget_id]

    def _set_foldout_state(self, widget_id, value):
        self._foldout_state[widget_id] = value
        self.dock.set_dirty()
        self.dock.show()

    def end_foldout_header_group(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

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
            computed_color = box_color if box_color else self._compute_box_color()
            group_box.setStyleSheet(
                f"QGroupBox {{ border: 1px solid {computed_color}; padding: 5px; }}"
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
    # SPACE METHODS (Unity-like GUILayout.Space and FlexibleSpace)
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
