from PyQt6.QtWidgets import QComboBox

from manim_studio.value_trackers.string_value_tracker import StringValueTracker


class DropdownWidget(QComboBox):
    """A dropdown widget to change a string property among a list of values."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.currentTextChanged.connect(self.value_tracker.set_value)
