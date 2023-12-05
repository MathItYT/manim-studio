from PyQt6.QtCore import QThread
from .live_scene import LiveScene


class RenderThread(QThread):
    def __init__(self, scene: LiveScene):
        super().__init__()
        self.scene = scene

    def run(self):
        self.scene.render()
