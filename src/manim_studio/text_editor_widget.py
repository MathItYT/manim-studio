from PyQt6.QtWidgets import QTextEdit

from .string_value_tracker import StringValueTracker


class TextEditorWidget(QTextEdit):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.textChanged.connect(
            lambda: self.value_tracker.set_value(self.toPlainText()))
        self.setPlaceholderText(name)
