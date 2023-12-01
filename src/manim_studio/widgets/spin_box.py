from PyQt6.QtWidgets import QDoubleSpinBox, QLabel
from manim import ValueTracker
import sys


class SpinBox(QDoubleSpinBox):
    """A spin box widget to edit a float property."""

    def __init__(self, name: str, default_value: float = 0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # It must be signed
        self.setRange(-sys.float_info.max, sys.float_info.max)
        self.name = name
        self.value_tracker = ValueTracker(default_value)
        self.valueChanged.connect(self.value_tracker.set_value)
