from typing import Union
from types import NoneType

from PyQt6.QtWidgets import QDialog, QGridLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

from manim import Mobject

from PIL.ImageQt import ImageQt

from .api import ManimStudioAPI


class MobjectPicker(QDialog):
    def __init__(self, window_width: int, aspect_ratio: float, mobject_class: type[Mobject]):
        super().__init__()
        self.setLayout(QGridLayout())
        self.selected_mobject = None
        self.setWindowTitle("Mobject Picker")
        
        self.mobjects_available = {k: v for k, v in ManimStudioAPI.scope.items() if isinstance(v, mobject_class)}
        self.mobjects_buttons = {}

        for i, (name, mobject) in enumerate(self.mobjects_available.items()):
            icon = QIcon(QPixmap.fromImage(ImageQt(mobject.get_image())))
            button = QPushButton(icon, None)
            button.setIconSize(QSize(window_width // 3, int(window_width // 3 / aspect_ratio)))
            button.setFixedWidth(window_width // 3)
            button.setFixedHeight(int(button.width() / aspect_ratio))
            self.layout().addWidget(button, i // 3, i % 3)
            self.mobjects_buttons[button] = mobject
            button.clicked.connect(lambda: self.select_mobject(name))

    def select_mobject(self, name: str):
        self.selected_mobject = name, self.mobjects_available[name]
        self.close()
    
    def wait_for_selection(self) -> Union[NoneType, tuple[str, Mobject]]:
        self.exec()
        return self.selected_mobject
