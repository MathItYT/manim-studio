from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QPixmap, QImage
import numpy as np

from .communicate import Communicate
from .live_scene import LiveScene
from .render_thread import RenderThread
from manim._config import config


class PreviewWidget(QWidget):
    """A widget to preview the final result."""

    def __init__(self, communicate: Communicate, scene: LiveScene, screen_size: tuple, preview, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicate = communicate
        self.scene = scene
        self.setWindowTitle("Manim Studio - Preview")
        if config.pixel_height > config.pixel_width:
            self.height_ = min(config.pixel_height, screen_size[1])
            self.width_ = self.height_ * config.pixel_width // config.pixel_height
        else:
            self.width_ = min(config.pixel_width, screen_size[0])
            self.height_ = self.width_ * config.pixel_height // config.pixel_width
        self.setGeometry(0, 0, self.width_, self.height_)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.label)
        self.setLayout(self.layout_)
        self.render_thread = RenderThread(self.scene, preview)
        self.render_thread.start()
        self.communicate.update_image.connect(self.update_image)
        self.communicate.update_image.emit(self.scene.renderer.get_frame())

    @pyqtSlot(np.ndarray)
    def update_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888)).scaledToHeight(self.height_, Qt.TransformationMode.SmoothTransformation))
