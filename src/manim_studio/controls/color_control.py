from manim_studio.value_trackers.color_value_tracker import ColorValueTracker
from PyQt6.QtWidgets import (
    QColorDialog,
    QLabel,
    QGroupBox,
    QVBoxLayout
)
from PyQt6.QtGui import QColor
from manim_studio.communicate import Communicate
import numpy as np


class ColorControl(QGroupBox):
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
        self.value_tracker = ColorValueTracker()
        self.color_picker = QColorDialog()
        self.color_picker.setOption(
            QColorDialog.ColorDialogOption.ShowAlphaChannel)
        self.color_picker.setOption(
            QColorDialog.ColorDialogOption.NoButtons)
        self.color_picker.setCurrentColor(QColor(0, 0, 0, 255))
        self.color_picker.currentColorChanged.connect(
            self.change_color_command)
        self.layout().addWidget(self.color_picker)

    def change_color_command(self, color: QColor):
        self.__communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).set_value(np.array([{color.red() / 255}, {color.green() / 255}, {color.blue() / 255}, {color.alpha() / 255}]))")
