from PyQt6.QtWidgets import QPushButton
from manim_studio.communicate import Communicate


class Button(QPushButton):
    def __init__(self, communicate: Communicate, name: str, callback: str):
        super().__init__()
        self.name = name
        self.callback = callback
        self.__communicate = communicate
        self.init_ui()

    def init_ui(self):
        self.setText(self.name)
        self.clicked.connect(
            lambda: self.__communicate.update_scene.emit(self.callback))

    def to_dict(self):
        return {
            "class": "Button",
            "name": self.name,
            "callback": self.callback
        }

    @classmethod
    def from_dict(cls, communicate: Communicate, data: dict):
        return cls(communicate, data["name"], data["callback"])
