from PyQt6.QtWidgets import QLineEdit

from .string_value_tracker import StringValueTracker


class LineEditorWidget(QLineEdit):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.textChanged.connect(self.value_tracker.set_value)
        self.setPlaceholderText(name)
