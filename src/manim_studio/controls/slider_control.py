from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider
)
from PyQt6.QtCore import Qt
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from manim_studio.communicate import Communicate


class SliderControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str, range: tuple[int, int], step: int, default: int):
        super().__init__()
        self.name = name
        self.range = range
        self.step = step
        self.default = default
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.slider_group = QGroupBox()
        self.slider_group.setLayout(QHBoxLayout(self.slider_group))
        self.min_ = QLabel(f"Minimum: {self.range[0]}")
        self.slider_group.layout().addWidget(self.min_)
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setRange(*self.range)
        self.slider.setSingleStep(self.step)
        self.slider.setValue(self.default)
        self.slider_group.layout().addWidget(self.slider)
        self.max_ = QLabel(f"Maximum: {self.range[1]}")
        self.slider_group.layout().addWidget(self.max_)
        self.layout().addWidget(self.slider_group)
        self.value_label = QLabel(f"Value: {self.default}")
        self.layout().addWidget(self.value_label)
        self.value_tracker = IntValueTracker(self.default)
        self.slider.valueChanged.connect(lambda: self.value_label.setText(
            f"Value: {self.slider.value()}"))
        self.slider.valueChanged.connect(lambda: self.__communicate.update_scene.emit(
            f"if hasattr(self, {self.name.__repr__()}): getattr(self, {self.name.__repr__()}).set_value({self.slider.value()})"))
        self.layout().addWidget(self.slider)

    def to_dict(self):
        return {
            "class": "SliderControl",
            "name": self.name,
            "value": self.slider.value(),
            "range": self.range,
            "step": self.step
        }

    @classmethod
    def from_dict(cls, communicate: Communicate, data: dict):
        slider_control = cls(
            communicate, data["name"], data["range"], data["step"], data["value"])
        slider_control.slider.setValue(data["value"])
        return slider_control
