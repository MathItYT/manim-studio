from PyQt6.QtWidgets import (
    QGroupBox,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QLabel
)
from manim_studio.communicate import Communicate
from manim_studio.value_trackers.string_value_tracker import StringValueTracker


class FileControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str):
        super().__init__()
        self.name = name
        self.file_name = ""
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        self.layout().addWidget(self.file_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_file)
        self.layout().addWidget(self.clear_button)
        self.value_tracker = StringValueTracker()
        self.clear_button.setEnabled(False)
        self.file_name_label = QLabel("Current File: ")
        self.layout().addWidget(self.file_name_label)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            self.select_file_command(file_name)

    def select_file_command(self, file_name: str):
        self.file_name = file_name
        self.file_name_label.setText("Current File: " + file_name)
        self.__communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).set_value({file_name.__repr__()})")
        self.clear_button.setEnabled(True)

    def clear_file(self):
        self.file_name = ""
        self.__communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).set_value('')")
        self.clear_button.setEnabled(False)
        self.file_name_label.setText("Current File: ")
