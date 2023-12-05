from PyQt6.QtWidgets import (
    QTextEdit,
    QLabel,
    QGroupBox,
    QVBoxLayout
)
from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from manim_studio.communicate import Communicate


class TextControl(QGroupBox):
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
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter your text here")
        self.value_tracker = StringValueTracker()
        self.text_edit.textChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"getattr(self, {self.name.__repr__()}).set_value('{self.text_edit.toPlainText().__repr__()}')"))
        self.layout().addWidget(self.text_edit)
