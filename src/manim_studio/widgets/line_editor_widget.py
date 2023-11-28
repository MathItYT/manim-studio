from PyQt6.QtWidgets import QLineEdit

from manim_studio.value_trackers.string_value_tracker import StringValueTracker


class LineEditorWidget(QLineEdit):
    """A line editor widget to edit a string property only using one line."""

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.textChanged.connect(self.value_tracker.set_value)
        self.setPlaceholderText(name)
