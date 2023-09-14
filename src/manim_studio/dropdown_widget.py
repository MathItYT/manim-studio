from PyQt6.QtWidgets import QComboBox

from .string_value_tracker import StringValueTracker


class DropdownWidget(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.currentTextChanged.connect(self.value_tracker.set_value)
