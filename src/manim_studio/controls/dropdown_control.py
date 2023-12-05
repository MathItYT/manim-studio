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
from manim_studio.value_trackers.list_value_tracker import ListValueTracker
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
        self.list_value_tracker = ListValueTracker(self.items)
        self.dropdown.currentTextChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"getattr(self, {self.name.__repr__()}).set_value({self.dropdown.currentText().__repr__()})"))
        self.add_option_button = QPushButton("Add Option")
        self.add_option_button.clicked.connect(self.add_option_command)
        self.layout().addWidget(self.dropdown)
        self.layout().addWidget(self.add_option_button)
        self.remove_option_button = QPushButton("Remove Option")
        self.remove_option_button.clicked.connect(self.remove_option_command)
        self.layout().addWidget(self.remove_option_button)

    def add_item(self, item: str):
        self.dropdown.addItem(item)
        self.items.append(item)
        self.__communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}_items).set_value({self.items.__repr__()})")

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

    def remove_option_command(self):
        dialog = QDialog()
        dialog.setWindowTitle("Remove Option")
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.label = QLabel("Select the option to remove:")
        dialog.layout().addWidget(dialog.label)
        dialog.dropdown = QComboBox()
        dialog.dropdown.addItems(self.items)
        dialog.layout().addWidget(dialog.dropdown)
        dialog.button = QPushButton("Remove")
        dialog.button.clicked.connect(lambda: self.remove_item(
            dialog.dropdown.currentText()) if dialog.dropdown.currentText() != "" else None)
        dialog.button.clicked.connect(dialog.close)
        dialog.layout().addWidget(dialog.button)
        dialog.exec()

    def remove_item(self, item: str):
        self.dropdown.removeItem(self.dropdown.findText(item))
        self.items.remove(item)
        self.__communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}_items).set_value({self.items.__repr__()})")
