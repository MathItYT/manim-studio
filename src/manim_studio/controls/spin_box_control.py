from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QLabel,
    QGroupBox,
    QVBoxLayout
)
from manim_studio.value_trackers.float_value_tracker import FloatValueTracker
from manim_studio.communicate import Communicate


class SpinBoxControl(QGroupBox):
    def __init__(self, communicate: Communicate, name: str, default: float = 0, min: float = 0, max: float = 100):
        super().__init__()
        self.name = name
        self.default = default
        self.min = min
        self.max = max
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.name)
        self.layout().addWidget(self.name_label)
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setMinimum(self.min)
        self.spin_box.setMaximum(self.max)
        self.spin_box.setValue(self.default)
        self.value_tracker = FloatValueTracker(self.default)
        self.spin_box.valueChanged.connect(
            lambda: self.__communicate.update_scene.emit(
                f"getattr(self, {self.name.__repr__()}).set_value({self.spin_box.value()})"))
        self.layout().addWidget(self.spin_box)
