from PyQt6.QtWidgets import QCheckBox
from manim_studio.value_trackers.boolean_value_tracker import BooleanValueTracker
from manim_studio.communicate import Communicate


class CheckboxControl(QCheckBox):
    def __init__(self, communicate: Communicate, name: str, default: bool = False):
        super().__init__()
        self.name = name
        self.default = default
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.value_tracker = BooleanValueTracker(self.default)
        self.setText(self.name)
        self.setChecked(self.default)
        self.stateChanged.connect(
            lambda: self.__communicate.update_scene.emit(f"getattr(self, {self.name.__repr__()}).set_value({self.isChecked()})"))
