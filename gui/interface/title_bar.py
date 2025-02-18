# interface/title_bar.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenuBar
from PyQt5.QtCore import Qt

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent  # Reference to the main window

        self.setFixedHeight(30)
        # Adjust the background/foreground colors as you prefer
        self.setStyleSheet("background-color: #444444; color: white;")

        #
        # 1. Create the menu bar
        #
        self.menuBar = QMenuBar(self)
        # Optional styling for the menu bar:
        self.menuBar.setStyleSheet("""
            QMenuBar {
                background-color: #444444;
                color: white;
            }
            QMenuBar::item {
                background-color: #444444;
            }
            QMenuBar::item:selected {
                background-color: #555555;
            }
        """)

        #
        # 2. (Optional) Create a label to show an app title in the title bar
        #
        self.titleLabel = QLabel("Robocom", self)
        self.titleLabel.setStyleSheet("padding-left: 10px;")  # a bit of spacing
        self.titleLabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        #
        # 3. Create window control buttons
        #
        self.minButton = QPushButton("-", self)
        self.maxButton = QPushButton("+", self)
        self.closeButton = QPushButton("x", self)
        for btn in (self.minButton, self.maxButton, self.closeButton):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("background-color: #555555; border: none; color: white;")

        #
        # 4. Lay everything out in one row
        #
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        # Add the label (or skip it if you don’t need a text title)
        layout.addWidget(self.titleLabel)

        # Add the menu bar
        layout.addWidget(self.menuBar)

        # Expand empty space between the menu and the window controls
        layout.addStretch()

        # Add the three window control buttons
        layout.addWidget(self.minButton)
        layout.addWidget(self.maxButton)
        layout.addWidget(self.closeButton)

        self.setLayout(layout)

        #
        # 5. Connect signals for the window controls
        #
        self.minButton.clicked.connect(self.minimize)
        self.maxButton.clicked.connect(self.maximize)
        self.closeButton.clicked.connect(self.close)

        # For dragging the window
        self._mouse_pos = None

    def minimize(self):
        if self._parent:
            self._parent.showMinimized()
            
    def maximize(self):
        if self._parent:
            if self._parent.isMaximized():
                self._parent.showNormal()
            else:
                self._parent.showMaximized()
                
    def close(self):
        if self._parent:
            self._parent.close()

    #
    # 6. Implement click-drag to move the frameless window
    #
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._parent:
            self._mouse_pos = event.globalPos() - self._parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self._mouse_pos and event.buttons() == Qt.LeftButton and self._parent:
            self._parent.move(event.globalPos() - self._mouse_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self._mouse_pos = None
        event.accept()
