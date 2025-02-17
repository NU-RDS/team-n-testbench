import PyQt5.sip as sip
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
        The dock is expected to have a .layout attribute.
        """
        self.dock = imdock
        self._layout_stack = [self.dock.layout]
        self._current_layout = self.dock.layout

        # Persistent widget storage.
        self._instance_buttons = {}   # label -> QPushButton
        self._state_button = {}       # label -> bool

        self._instance_toggles = {}   # label -> QCheckBox
        self._state_toggle = {}       # label -> bool

        self._instance_labels = {}    # key -> QLabel

    def _get_button(self, label):
        if label not in self._instance_buttons or sip.isdeleted(self._instance_buttons[label]):
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, l=label: self._on_button_clicked(l))
            self._instance_buttons[label] = btn
            self._state_button[label] = False
            self._current_layout.addWidget(btn)
        else:
            btn = self._instance_buttons[label]
            # If for some reason the widget is not in the current layout, add it.
            if btn.parent() is None:
                self._current_layout.addWidget(btn)
        return btn

    def button(self, label, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        btn = self._get_button(label)
        apply_style(btn, text_color, bg_color, font_size, extra_styles)
        self.dock.set_dirty()
        was_clicked = self._state_button[label]
        self._state_button[label] = False  # Reset one-shot click flag.
        return was_clicked

    def _on_button_clicked(self, label):
        print(f"Button '{label}' clicked!")
        self._state_button[label] = True
        self.dock.set_dirty()
        self.dock.show()

    def _get_toggle(self, label, initial_value):
        if label not in self._instance_toggles or sip.isdeleted(self._instance_toggles[label]):
            chk = QCheckBox(label)
            chk.setChecked(initial_value)
            chk.stateChanged.connect(lambda state, l=label: self._on_toggle_changed(l, state))
            self._instance_toggles[label] = chk
            self._state_toggle[label] = chk.isChecked()
            self._current_layout.addWidget(chk)
        else:
            chk = self._instance_toggles[label]
            if chk.parent() is None:
                self._current_layout.addWidget(chk)
        return chk

    def toggle(self, label, initial_value=False, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        chk = self._get_toggle(label, initial_value)
        apply_style(chk, text_color, bg_color, font_size, extra_styles)
        self.dock.set_dirty()
        return self._state_toggle[label]

    def _on_toggle_changed(self, label, state):
        self._state_toggle[label] = (state == Qt.Checked)
        print(f"Toggle '{label}' changed to {self._state_toggle[label]}")
        self.dock.set_dirty()
        self.dock.show()

    def _get_label(self, key, text):
        if key not in self._instance_labels or sip.isdeleted(self._instance_labels[key]):
            lbl = QLabel(text)
            self._instance_labels[key] = lbl
            self._current_layout.addWidget(lbl)
        else:
            lbl = self._instance_labels[key]
        return lbl

    def label(self, text, text_color=None, bg_color=None, font_size=None, extra_styles=""):
        key = text  # Here we use text as the key; you could allow a custom key if desired.
        lbl = self._get_label(key, text)
        lbl.setText(text)
        apply_style(lbl, text_color, bg_color, font_size, extra_styles)
        self.dock.set_dirty()
        return lbl

    def begin_horizontal(self):
        h_layout = QHBoxLayout()
        self._current_layout.addLayout(h_layout)
        self._layout_stack.append(h_layout)
        self._current_layout = h_layout

    def end_horizontal(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def begin_vertical(self):
        v_layout = QVBoxLayout()
        self._current_layout.addLayout(v_layout)
        self._layout_stack.append(v_layout)
        self._current_layout = v_layout

    def end_vertical(self):
        if len(self._layout_stack) > 1:
            self._layout_stack.pop()
            self._current_layout = self._layout_stack[-1]

    def reset(self):
        for key in self._state_button:
            self._state_button[key] = False
