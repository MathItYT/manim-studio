from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QDialog,
    QLineEdit
)
from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from manim_studio.communicate import Communicate


class DropdownControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str, items: list[str]):
        super().__init__()
        self.name = name
        self.items = items
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.dropdown = QComboBox()
        self.dropdown.addItems(self.items)
        self.value_tracker = StringValueTracker(self.dropdown.currentText())
        self.dropdown.currentTextChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"getattr(self, {self.name.__repr__()}).set_value('{self.dropdown.currentText().__repr__()}')"))
        self.add_option_button = QPushButton("Add Option")
        self.add_option_button.clicked.connect(self.add_option_command)
        self.layout().addWidget(self.dropdown)

    def add_item(self, item: str):
        self.dropdown.addItem(item)
        self.items.append(item)

    def add_option_command(self):
        dialog = QDialog()
        dialog.setWindowTitle("Add Option")
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.label = QLabel("Enter the option name:")
        dialog.layout().addWidget(dialog.label)
        dialog.line_edit = QLineEdit()
        dialog.layout().addWidget(dialog.line_edit)
        dialog.button = QPushButton("Add")
        dialog.button.clicked.connect(lambda: self.add_item(
            dialog.line_edit.text()) if dialog.line_edit.text() != "" else None)
        dialog.button.clicked.connect(dialog.close)
        dialog.layout().addWidget(dialog.button)
        dialog.exec()
