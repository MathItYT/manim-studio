from PyQt6.QtWidgets import QSlider

from manim_studio.value_trackers.int_value_tracker import IntValueTracker


class Slider(QSlider):
    """
    A slider widget to edit an integer property
    that can be set to a value between a minimum and a maximum.
    There's also a step value that can be set.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = IntValueTracker(0)
        self.valueChanged.connect(self.value_tracker.set_value)
