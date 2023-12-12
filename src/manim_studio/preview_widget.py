from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from .communicate import Communicate
from manim import config, Mobject
from .render_thread import RenderThread
import numpy as np


def convert_to_manim_coords(x: int, y: int, label: QLabel) -> tuple[float, float]:
    w, h = label.width(), label.height()
    top_left = label.mapToGlobal(label.rect().topLeft())
    x -= top_left.x()
    y -= top_left.y()
    x = x / w * config.frame_width - config.frame_width / 2
    y = (h - y) / h * config.frame_height - config.frame_height / 2
    return x, y


class PreviewWidget(QWidget):
    def __init__(self, communicate: Communicate, screen_size: tuple[int, int], render_thread: RenderThread):
        super().__init__()
        self.setWindowTitle("Preview")
        self.communicate = communicate
        self.w, self.h = screen_size
        self.interactive_mobjects: dict[str, Mobject] = {}
        self.communicate.update_image.connect(self.update_image)
        self.communicate.enable_interact.connect(self.enable_interact)
        self.communicate.add_to_interactive_mobjects.connect(
            self.add_to_interactive_mobjects)
        self.communicate.remove_from_interactive_mobjects.connect(
            self.remove_from_interactive_mobjects)
        self.render_thread = render_thread
        self.enable = False
        self.scene = self.render_thread.scene
        self.init_ui()

    def add_to_interactive_mobjects(self, name: str):
        if name in self.interactive_mobjects:
            return
        self.interactive_mobjects[name] = getattr(self.scene, name)

    def remove_from_interactive_mobjects(self, name: str):
        if name not in self.interactive_mobjects:
            return
        del self.interactive_mobjects[name]

    def enable_interact(self, enable: bool):
        self.enable = enable
        if not hasattr(self.scene, "mouse"):
            self.communicate.update_scene.emit(
                "self.mouse = DotTracker()")

    def interact(self, event: QMouseEvent):
        if not self.enable:
            return
        pos = event.pos()
        x, y = pos.x(), pos.y()
        x, y = convert_to_manim_coords(x, y, self.preview_label)
        self.communicate.update_scene.emit(
            f"self.mouse.move_to(np.array([{x}, {y}, 0]))")
        if event.buttons() != Qt.MouseButton.LeftButton:
            return
        for name, mobject in self.interactive_mobjects.items():
            center, width, height = mobject.get_center(), mobject.width, mobject.height
            if center[0] - width / 2 <= x <= center[0] + width / 2 and center[1] - height / 2 <= y <= center[1] + height / 2:
                self.communicate.update_scene.emit(f"getattr(self, {name.__repr__()}).move_to(self.mouse.get_center())")
                break

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.init_preview_label()
        self.render_thread.start()

    def init_preview_label(self):
        self.preview_label = QLabel()
        w, h = config.pixel_width, config.pixel_height
        aspect_ratio = w / h
        h = min(h, self.h)
        w = int(h * aspect_ratio)
        w = min(w, self.w)
        h = int(w / aspect_ratio)
        self.preview_label.setFixedSize(w, h)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setGeometry(0, 0, w, h)
        self.w = w
        self.h = h
        self.layout().addWidget(self.preview_label)
        self.preview_label.mouseMoveEvent = self.interact

    def update_image(self, image: np.ndarray):
        self.preview_label.setPixmap(QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888)).scaledToHeight(self.h, Qt.TransformationMode.SmoothTransformation))
