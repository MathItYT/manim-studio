from manim_studio.value_trackers.bytes_value_tracker import BytesValueTracker
from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from PyQt6.QtWidgets import QFileDialog, QGroupBox, QVBoxLayout, QPushButton, QLabel
import os


class FileWidget(QGroupBox):
    def __init__(self, name: str, file_flags: str = "All Files (*)", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.setTitle(self.name)
        self.file_flags = file_flags or "All Files (*)"
        self.file_path = StringValueTracker("")
        self.file_size = IntValueTracker(0)

        self.name_label = QLabel(self.name)
        self.file_path_label = QLabel()
        self.file_size_label = QLabel()
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        self.clear_file_button = QPushButton("Clear File")
        self.clear_file_button.clicked.connect(self.clear_file)
        self.clear_file_button.setEnabled(False)
        self.value_tracker = BytesValueTracker(b"")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.file_path_label)
        self.layout.addWidget(self.file_size_label)
        self.layout.addWidget(self.select_file_button)
        self.layout.addWidget(self.clear_file_button)
        self.setLayout(self.layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.file_flags
        )
        if file_path:
            self.select_file_command(file_path)

    def select_file_command(self, file_path: str):
        self.file_path.set_value(file_path)
        self.file_path_label.setText(self.file_path.get_value())
        self.file_size.set_value(
            os.path.getsize(self.file_path.get_value()))
        self.file_size_label.setText(
            f"File Size: {self.file_size.get_value()} bytes")
        self.clear_file_button.setEnabled(True)
        with open(file_path, "rb") as f:
            self.value_tracker.set_value(f.read())

    def clear_file(self):
        self.file_path.set_value("")
        self.file_path_label.setText("")
        self.file_size.set_value(0)
        self.file_size_label.setText("")
        self.clear_file_button.setEnabled(False)
        self.value_tracker.set_value(b"")
