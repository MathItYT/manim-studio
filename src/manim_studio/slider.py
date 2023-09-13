from PyQt6.QtWidgets import QSlider

from .int_value_tracker import IntValueTracker


class Slider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = IntValueTracker(0)
        self.valueChanged.connect(self.value_tracker.set_value)
