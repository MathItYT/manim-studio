from typing import Union
from copy import copy

from PyQt6.QtWidgets import QDialog, QGridLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

from manim import Mobject, Camera

from PIL.ImageQt import ImageQt

from .api import ManimStudioAPI


class MobjectPicker(QDialog):
    def __init__(
        self,
        window_width: int,
        camera: Camera,
        mobject_class: type[Mobject]
    ):
        super().__init__()
        self.setLayout(QGridLayout())
        self.selected_mobject = None
        self.setWindowTitle("Mobject Picker")
        aspect_ratio = camera.frame_width / camera.frame_height

        self.mobjects_available = {k: v
                                   for k, v in ManimStudioAPI.scene.__dict__.items()
                                   if isinstance(v, mobject_class)}

        for i, (name, mobject) in enumerate(self.mobjects_available.items()):
            icon = QIcon(QPixmap.fromImage(ImageQt(mobject.get_image(Camera(
                frame_width=camera.frame_width,
                frame_height=camera.frame_height,
                background_color=camera.background_color,
                pixel_width=camera.pixel_width,
                pixel_height=camera.pixel_height
            )))))
            button = QPushButton(icon, None)
            button.setIconSize(
                QSize(window_width // 3, int(window_width // 3 / aspect_ratio)))
            button.setFixedSize(window_width // 3,
                                int(window_width // 3 / aspect_ratio))
            self.layout().addWidget(button, i // 3, i % 3)
            button.clicked.connect(self.get_select_mobject_func(name))

    def get_select_mobject_func(self, name: str):
        def select_mobject():
            self.selected_mobject = name, self.mobjects_available[name]
            self.close()
        return select_mobject

    def wait_for_selection(self) -> Union[tuple[str, Mobject], None]:
        self.exec()
        return self.selected_mobject
