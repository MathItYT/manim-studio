from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from PyQt6.QtWidgets import (
    QLineEdit,
    QLabel,
    QGroupBox,
    QVBoxLayout
)
from manim_studio.communicate import Communicate


class LineControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str):
        super().__init__()
        self.name = name
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter your single line text here")
        self.value_tracker = StringValueTracker()
        self.line_edit.textChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"getattr(self, {self.name.__repr__()}).set_value({self.line_edit.text().__repr__()})"))
        self.layout().addWidget(self.line_edit)
