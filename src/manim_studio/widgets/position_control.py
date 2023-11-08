from PyQt6.QtWidgets import QDoubleSpinBox, QGroupBox, QHBoxLayout, QCheckBox
from manim import Dot
from manim_studio.live_scene import LiveScene
import numpy as np


class PositionControl(QGroupBox):
    def __init__(self, name: str, live_scene: LiveScene, default: np.ndarray = np.array([0, 0, 0])):
        self.name = name
        self.default = default
        self.live_scene = live_scene
        super().__init__(name)
        self.x_ = QDoubleSpinBox()
        self.y_ = QDoubleSpinBox()
        self.z_ = QDoubleSpinBox()
        self.display_dot_checkbox = QCheckBox("Display Dot")
        self.display_dot_checkbox.setChecked(False)
        self.display_dot_checkbox.stateChanged.connect(
            lambda: self.display_dot(self.display_dot_checkbox.isChecked()))
        self.dot = Dot(self.default).set_opacity(0)
        setattr(self.live_scene, self.name, self.dot)
        self.live_scene.add(getattr(self.live_scene, self.name))
        self.x_.setValue(default[0])
        self.y_.setValue(default[1])
        self.z_.setValue(default[2])
        self.x_.valueChanged.connect(self.update_x)
        self.y_.valueChanged.connect(self.update_y)
        self.z_.valueChanged.connect(self.update_z)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.x_)
        self.layout().addWidget(self.y_)
        self.layout().addWidget(self.z_)
        self.layout().addWidget(self.display_dot_checkbox)

    def update_x(self, value: int):
        self.default[0] = value
        self.dot.set_x(value)

    def update_y(self, value: int):
        self.default[1] = value
        self.dot.set_y(value)

    def update_z(self, value: int):
        self.default[2] = value
        self.dot.set_z(value)

    def display_dot(self, display: bool):
        if display:
            self.dot.set_opacity(1)
        else:
            self.dot.set_opacity(0)
