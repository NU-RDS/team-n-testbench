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
    QSlider,
    QLineEdit,
    QComboBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from enum import Enum


class FontStyle(Enum):
    NORMAL = 0
    BOLD = 1
    ITALIC = 2
    BOLD_ITALIC = 3

class LayoutAlignment(Enum):
    LEFT = Qt.AlignLeft
    RIGHT = Qt.AlignRight
    CENTER = Qt.AlignCenter
    TOP = Qt.AlignTop
    BOTTOM = Qt.AlignBottom
    TOP_LEFT = Qt.AlignTop | Qt.AlignLeft
    TOP_RIGHT = Qt.AlignTop | Qt.AlignRight
    BOTTOM_LEFT = Qt.AlignBottom | Qt.AlignLeft
    BOTTOM_RIGHT = Qt.AlignBottom | Qt.AlignRight


def apply_style(widget, text_color=None, bg_color=None, font_size=None, extra_styles="", font_style=FontStyle.NORMAL):
    styles = []

    if text_color:
        styles.append(f"color: {text_color};")
    if bg_color:
        styles.append(f"background-color: {bg_color};")
    if font_size:
        styles.append(f"font-size: {font_size}px;")
    if font_style in (FontStyle.BOLD, FontStyle.BOLD_ITALIC):
        styles.append("font-weight: bold;")
    if font_style in (FontStyle.ITALIC, FontStyle.BOLD_ITALIC):
        styles.append("font-style: italic;")
    if extra_styles:
        if isinstance(extra_styles, str):
            styles.append(extra_styles)
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
        self._text_field_state = {}
        self._slider_state = {}  # Map: unique widget ID -> int
        self._slider_labels = {} # Map: unique widget ID -> QLabel displaying slider value
        self._dropdown_state = {} # Map: unique widget ID -> int
        self._scroll_flags = {}    # maps scroll id -> bool (True means "keep at bottom")
        self._scroll_amount = {}  # maps scroll id -> QScrollArea
        self._scroll_widget = {}  # maps scroll id -> QWidget
        self._scroll_stack = []  # stack of scroll widgets ids
        self._key_counter = {}

    def start(self):
        """Resets the key counters and layout stack."""
        self._key_counter = {}
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

    def _get_key(self, base_key):
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
    def label(self, text, text_color=None, bg_color=None, font_size=None, extra_styles="", font_style=FontStyle.NORMAL):
        widget_id = self._get_key(text)
        # make sure the label is not bytes
        text = str(text)
        lbl = QLabel(text)
        apply_style(lbl, text_color, bg_color, font_size, extra_styles, font_style=font_style)
        self._current_layout.addWidget(lbl)
        self.dock.set_dirty()
        return lbl

    # --------------------------------------------------------------------------
    # TEXT FIELD
    # --------------------------------------------------------------------------
    def text_field(self, label, initial_value="", placeholder="", text_color=None, bg_color=None, font_size=None, extra_styles="", font_style=FontStyle.NORMAL):
        widget_id = self._get_key(label)
        if widget_id not in self._text_field_state:
            self._text_field_state[widget_id] = initial_value

        field = QLineEdit()
        field.setText(self._text_field_state[widget_id])
        if placeholder:
            field.setPlaceholderText(placeholder)
        apply_style(field, text_color, bg_color, font_size, extra_styles, font_style=font_style)
        field.textChanged.connect(lambda text, wid=widget_id: self._set_text_field_state(wid, text))
        self._current_layout.addWidget(field)
        self.dock.set_dirty()
        return self._text_field_state[widget_id]

    def _set_text_field_state(self, widget_id, text):
        self._text_field_state[widget_id] = text
        self.dock.set_dirty()
        self.dock.show()

    # --------------------------------------------------------------------------
    # SLIDER FIELD (with value display)
    # --------------------------------------------------------------------------
    def slider(self, label, initial_value, min_value, max_value, orientation=Qt.Horizontal,
               text_color=None, bg_color=None, font_size=None, extra_styles=""):
        """
        Creates a slider field with a numeric display next to it.
        Returns the current slider value.
        """
        widget_id = self._get_key(label)
        if widget_id not in self._slider_state:
            self._slider_state[widget_id] = initial_value

        # Create a horizontal layout to hold slider and value label.
        h_layout = QHBoxLayout()
        slider_widget = QSlider(orientation)
        slider_widget.setMinimum(min_value)
        slider_widget.setMaximum(max_value)
        slider_widget.setValue(self._slider_state[widget_id])
        slider_widget.valueChanged.connect(lambda value, wid=widget_id: self._set_slider_state(wid, value))
        slider_widget.sliderReleased.connect(lambda wid=widget_id: self._on_slider_release(wid))
        h_layout.addWidget(slider_widget)

        # Create a label to display the slider's current value.
        value_label = QLabel(str(self._slider_state[widget_id]))
        apply_style(value_label, text_color="white", bg_color="transparent", font_size=12)
        h_layout.addWidget(value_label)

        # Store the label for later updates.
        if not hasattr(self, "_slider_labels"):
            self._slider_labels = {}
        self._slider_labels[widget_id] = value_label

        self._current_layout.addLayout(h_layout)
        return self._slider_state[widget_id]

    def _set_slider_state(self, widget_id, value):
        self._slider_state[widget_id] = value
        # Update the label if it exists.
        if hasattr(self, "_slider_labels") and widget_id in self._slider_labels:
            self._slider_labels[widget_id].setText(str(value))
        # Optionally, you might mark the dock dirty here.
        # self.dock.set_dirty()

    def _on_slider_release(self, widget_id):
        self.dock.set_dirty()
        self.dock.show()

    # --------------------------------------------------------------------------
    # DROPDOWN FIELD
    # --------------------------------------------------------------------------

    def dropdown(self, label, options, initial_value=0, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        widget_id = self._get_key(label)

        if widget_id not in self._dropdown_state:
            self._dropdown_state[widget_id] = initial_value

        dropdown = QComboBox()
        dropdown.addItems(options)
        dropdown.setCurrentIndex(self._dropdown_state[widget_id])
        dropdown.currentIndexChanged.connect(lambda index, wid=widget_id: self._set_dropdown_state(wid, index))
        self._current_layout.addWidget(dropdown)
        self.dock.set_dirty()
        return self._dropdown_state[widget_id]
    
    def _set_dropdown_state(self, widget_id, index):
        self._dropdown_state[widget_id] = index
        self.dock.set_dirty()
        self.dock.show()


    # --------------------------------------------------------------------------
    # UTILITY
    # --------------------------------------------------------------------------
    def _compute_box_color(self):
        value = 200
        return f"rgb({value}, {value}, {value})"

    def _create_boxed_container(self, layout_class, indent=0, box_color=None):
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(1)
        frame_id = self._get_key("box")
        computed_color = box_color if box_color else self._compute_box_color()
        frame.setObjectName(frame_id)
        # make the height the minimum necessary to contain the layout
        frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        frame.setStyleSheet(f"QFrame#{frame_id} {{ border: 1px solid {computed_color}; padding: 5px; }}")
        layout = layout_class()
        layout.setContentsMargins(indent, 0, 0, 0)
        frame.setLayout(layout)
        return frame, layout

    # --------------------------------------------------------------------------
    # GROUPING METHODS (WITH OPTIONAL BOXING, INDENT, AND ALIGNMENT)
    # --------------------------------------------------------------------------
    def begin_horizontal(self, boxed=False, box_color=None, indent=0, alignment: LayoutAlignment = None):
        if boxed:
            container, layout = self._create_boxed_container(QHBoxLayout, indent, box_color)
            if alignment is not None:
                layout.setAlignment(alignment.value)
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
            h_layout = QHBoxLayout()
            if indent:
                h_layout.setContentsMargins(indent, 0, 0, 0)
            if alignment is not None:
                h_layout.setAlignment(alignment.value)
            self._current_layout.addLayout(h_layout)
            self._layout_stack.append(h_layout)
            self._current_layout = h_layout

    def begin_vertical(self, boxed=False, box_color=None, indent=0, alignment: LayoutAlignment = None):
        if boxed:
            container, layout = self._create_boxed_container(QVBoxLayout, indent, box_color)
            if alignment is not None:
                layout.setAlignment(alignment.value)
            self._current_layout.addWidget(container)
            self._layout_stack.append(layout)
            self._current_layout = layout
        else:
            v_layout = QVBoxLayout()
            if indent:
                v_layout.setContentsMargins(indent, 0, 0, 0)
            if alignment is not None:
                v_layout.setAlignment(alignment.value)
            self._current_layout.addLayout(v_layout)
            self._layout_stack.append(v_layout)
            self._current_layout = v_layout

    def end_horizontal(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def end_vertical(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    # --------------------------------------------------------------------------
    # SCROLLABLE REGION (with persistent scroll state)
    # --------------------------------------------------------------------------
    def begin_scroll(self, orientation=Qt.Vertical, scroll_id=None, keep_bottom=False, policy=None):
        # If no scroll_id is provided, generate one.
        if scroll_id is None:
            scroll_id = self._get_key("scroll")
        scroll_area = QScrollArea()
        if policy is not None:
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        if orientation == Qt.Vertical:
            container_layout = QVBoxLayout()
            # don't allow the horizontal scrollbar
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            container_layout = QHBoxLayout()
            # don't allow the vertical scrollbar
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        container.setLayout(container_layout)
        scroll_area.setWidget(container)


        # Connect the scrollbar's valueChanged signal to store its current value.
        scroll_area.verticalScrollBar().valueChanged.connect(
            lambda value, sid=scroll_id: self._on_scroll_value_changed(value, sid)
        )

        # Persist this scroll widget.
        self._scroll_widget[scroll_id] = scroll_area
        # If we haven't stored a scroll amount before, initialize it.
        if scroll_id not in self._scroll_amount.keys():
            self._scroll_amount[scroll_id] = 0
        # Store the keep_bottom flag.
        self._scroll_flags[scroll_id] = keep_bottom

        self._current_layout.addWidget(scroll_area)
        self._layout_stack.append(container_layout)
        self._current_layout = container_layout

        # Push this scroll_id onto our scroll stack.
        self._scroll_stack.append(scroll_id)
        return scroll_id

    def end_scroll(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def _update_scroll_values(self):
        for scroll_id in self._scroll_stack:
            if self._scroll_flags[scroll_id]:
                self._scroll_widget[scroll_id].verticalScrollBar().setValue(
                    self._scroll_widget[scroll_id].verticalScrollBar().maximum()
                )
            else:
                self._scroll_widget[scroll_id].verticalScrollBar().setValue(self._scroll_amount[scroll_id])

    def _on_scroll_value_changed(self, value, scroll_id):
        # Store the current scroll value.
        print(f"Scroll {scroll_id} value changed to {value}")
        self._scroll_amount[scroll_id] = value

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
        button.clicked.connect(lambda checked, wid=widget_id: self._on_foldout_toggled(checked, wid, title, button))
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

    def _on_foldout_toggled(self, checked, widget_id, title, button):
        self._set_foldout_state(widget_id, checked)
        new_arrow = "v" if checked else ">"
        button.setText(f"{new_arrow} {title}")

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
            group_box.setStyleSheet(f"QGroupBox {{ border: 1px solid {computed_color}; padding: 5px; }}")
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
