from PyQt6.QtWidgets import QPushButton
from manim_studio.communicate import Communicate


class Button(QPushButton):
    def __init__(self, callback: str, communicate: Communicate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.communicate = communicate
        self.clicked.connect(
            lambda: self.communicate.update_scene.emit(self.callback))
