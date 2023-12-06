from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout
)
from manim import Dot
from manim_studio.communicate import Communicate
from manim_studio.value_trackers.dot_tracker import DotTracker
import numpy as np
import sys


class PositionControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str, default: np.ndarray):
        super().__init__()
        self.name = name
        self.default = default
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.position_group_box = QGroupBox()
        self.position_group_box.setLayout(QHBoxLayout(self.position_group_box))
        self.position_group_box.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.position_group_box)
        self.x_spin_box = QDoubleSpinBox()
        self.x_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
        self.x_spin_box.setValue(self.default[0])
        self.position_group_box.layout().addWidget(self.x_spin_box)
        self.y_spin_box = QDoubleSpinBox()
        self.y_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
        self.y_spin_box.setValue(self.default[1])
        self.position_group_box.layout().addWidget(self.y_spin_box)
        self.z_spin_box = QDoubleSpinBox()
        self.z_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
        self.z_spin_box.setValue(self.default[2])
        self.position_group_box.layout().addWidget(self.z_spin_box)
        self.value_tracker = DotTracker(self.default)
        self.x_spin_box.valueChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"if hasattr(self, {self.name.__repr__()}): getattr(self, {self.name.__repr__()}).move_to(np.array([{self.x_spin_box.value()}, {self.y_spin_box.value()}, {self.z_spin_box.value()}]))"))
        self.y_spin_box.valueChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"if hasattr(self, {self.name.__repr__()}): getattr(self, {self.name.__repr__()}).move_to(np.array([{self.x_spin_box.value()}, {self.y_spin_box.value()}, {self.z_spin_box.value()}]))"))
        self.z_spin_box.valueChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"if hasattr(self, {self.name.__repr__()}): getattr(self, {self.name.__repr__()}).move_to(np.array([{self.x_spin_box.value()}, {self.y_spin_box.value()}, {self.z_spin_box.value()}]))"))

    def to_dict(self):
        return {
            "class": "PositionControl",
            "name": self.name,
            "position": np.ndarray([self.x_spin_box.value(), self.y_spin_box.value(), self.z_spin_box.value()])
        }

    @classmethod
    def from_dict(cls, communicate: Communicate, data: dict):
        position_control = cls(communicate, data["name"], data["position"])
        position_control.x_spin_box.setValue(data["position"][0])
        position_control.y_spin_box.setValue(data["position"][1])
        position_control.z_spin_box.setValue(data["position"][2])
        return position_control
