from PyQt6.QtWidgets import QCheckBox

from .boolean_value_tracker import BooleanValueTracker


class CheckboxWidget(QCheckBox):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = BooleanValueTracker(False)
        self.stateChanged.connect(
            lambda: self.value_tracker.set_value(self.isChecked()))
        self.setText(name)
