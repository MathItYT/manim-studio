from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QGroupBox
from PyQt6.QtGui import QPixmap, QImage
from manim import Mobject, Camera
from PyQt6.QtCore import Qt
from typing import Callable
import numpy as np


class ListOfMobjects(QScrollArea):
    def __init__(self, list_of_mobjects: Callable[[], Mobject], editor):
        super().__init__()
        self.setWindowTitle("Manim Studio - List of Mobjects")
        self.list_of_mobjects = list_of_mobjects
        self.editor = editor
        self.lists_of_submobjects = []
        self.initUI()

    def initUI(self):
        self.setWidgetResizable(True)
        self.setWidget(self._create_widget())
        list_mobjects = self.list_of_mobjects()
        list_mobjects = [
            mobject for mobject in list_mobjects if not type(mobject) == Mobject]
        self._create_buttons(list_mobjects)
        self._create_update_button()

    def _create_buttons(self, list_mobjects):
        for i, mobject in enumerate(list_mobjects):
            layout = QVBoxLayout()
            label = QLabel()
            label.setPixmap(QPixmap.fromImage(
                QImage(self._get_image(mobject), 200, 200, QImage.Format.Format_RGB888)))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label = QLabel(mobject.__class__.__name__)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            add_to_scene_button = QPushButton("Add to Scene")
            add_to_scene_button.clicked.connect(
                lambda: self.editor.scene.add(mobject))
            bring_to_back_button = QPushButton("Bring to Back")
            bring_to_back_button.clicked.connect(
                lambda: self.editor.scene.bring_to_back(mobject))
            remove_from_scene_button = QPushButton("Remove from Scene")
            remove_from_scene_button.clicked.connect(
                lambda: self.editor.scene.remove(mobject))
            list_of_submobjects = ListOfMobjects(
                lambda: mobject.submobjects, self.editor)
            self.lists_of_submobjects.append(list_of_submobjects)
            show_submobjects_button = QPushButton("Show Submobjects")
            show_submobjects_button.clicked.connect(
                lambda: list_of_submobjects.show())
            layout.addWidget(label)
            layout.addWidget(text_label)
            layout.addWidget(add_to_scene_button)
            layout.addWidget(bring_to_back_button)
            layout.addWidget(remove_from_scene_button)
            layout.addWidget(show_submobjects_button)
            groupbox = QGroupBox()
            groupbox.setLayout(layout)
            self.widget().layout().addWidget(groupbox, i // 3, i % 3)

    def _create_update_button(self):
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update)
        self.widget().layout().addWidget(update_button, len(
            self.list_of_mobjects()) // 3, 0, 1, 3)

    def _create_widget(self):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)
        return widget

    def update(self):
        for i in reversed(range(self.widget().layout().count())):
            self.widget().layout().itemAt(i).widget().setParent(None)
        self.initUI()

    def _get_image(self, mobject: Mobject):
        camera = Camera(
            pixel_width=200,
            pixel_height=200,
            frame_width=max(mobject.width + 0.1, mobject.height + 0.1),
            frame_height=max(mobject.width + 0.1, mobject.height + 0.1),
        )
        return np.array(mobject.get_image(camera=camera).convert("RGB"))
