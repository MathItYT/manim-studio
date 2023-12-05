from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea
)


class ControlsWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controls")
        self.init_ui()

    def init_ui(self):
        self.setWidget(QWidget())
        self.setWidgetResizable(True)
        self.widget().setLayout(QVBoxLayout(self.widget()))
        self.label = QLabel("No controls")
        self.widget().layout().addWidget(self.label)
        self.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.widget().layout().setSpacing(0)

    def add_controls(self, controls: QWidget):
        if self.label is not None:
            self.widget().layout().removeWidget(self.label)
            self.label = None
        self.widget().layout().addWidget(controls)
