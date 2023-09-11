from PyQt6.QtCore import QThread
from .live_scene import LiveScene


class RenderThread(QThread):
    def __init__(self, scene: LiveScene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = scene

    def run(self):
        self.scene.render()
