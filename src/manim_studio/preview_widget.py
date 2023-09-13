from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QPixmap, QImage
import numpy as np

from .communicate import Communicate
from .live_scene import LiveScene
from .render_thread import RenderThread


class PreviewWidget(QWidget):
    def __init__(self, communicate: Communicate, scene: LiveScene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicate = communicate
        self.scene = scene
        self.setWindowTitle("Manim Studio - Preview")
        self.setGeometry(0, 0, 1920, 1080)
        self.label = QLabel()
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.label.setGeometry(0, 0, 1920, 1080)
        self.label.setScaledContents(True)
        self.layout_.addWidget(self.label)
        self.setLayout(self.layout_)
        self.render_thread = RenderThread(self.scene)
        self.render_thread.start()
        self.communicate.update_image.connect(self.update_image)
        self.communicate.update_image.emit(self.scene.renderer.get_frame())

    @pyqtSlot(np.ndarray)
    def update_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888)))
        self.label.adjustSize()
