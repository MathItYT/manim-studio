from manim_studio.code_edit import CodeEdit
from manim_studio.value_trackers.string_value_tracker import StringValueTracker


class TextEditorWidget(CodeEdit):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_tracker = StringValueTracker("")
        self.textChanged.connect(
            lambda: self.value_tracker.set_value(self.toPlainText()))
