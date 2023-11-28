from PyQt6.QtCore import QThread
from .live_scene import LiveScene


class RenderThread(QThread):
    """A thread to render the scene."""

    def __init__(self, scene: LiveScene, preview: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preview = preview
        self.scene = scene

    def run(self):
        self.scene.render(self.preview)
