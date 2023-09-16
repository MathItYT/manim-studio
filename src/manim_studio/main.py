from PyQt6.QtWidgets import QApplication
from typing import Union
import sys

from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .live_scene import LiveScene
from .communicate import Communicate
from .ai_widget import AIWidget


def main(scene_type=LiveScene) -> None:
    app = QApplication(sys.argv)
    communicate = Communicate()
    scene = scene_type(communicate)
    editor_window = EditorWidget(communicate, scene)
    preview_window = PreviewWidget(communicate, scene)
    preview_window.showMaximized()
    editor_window.show()
    if AIWidget is not None:
        ai_window = AIWidget(communicate)
        ai_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(LiveScene)
