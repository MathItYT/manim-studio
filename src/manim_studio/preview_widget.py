from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from .communicate import Communicate
from manim import config
import numpy as np


class PreviewWidget(QWidget):
    def __init__(self, communicate: Communicate, screen_size: tuple[int, int]):
        super().__init__()
        self.setWindowTitle("Preview")
        self.communicate = communicate
        self.w, self.h = screen_size
        self.communicate.update_image.connect(self.update_image)
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.init_preview_label()

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

    def update_image(self, image: np.ndarray):
        self.preview_label.setPixmap(QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888)).scaledToHeight(self.h, Qt.TransformationMode.SmoothTransformation))
