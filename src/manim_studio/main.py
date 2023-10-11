from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys

from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .live_scene import LiveScene
from .communicate import Communicate
from .ai_widget import AIWidget
from .get_icon_file import get_icon_file


def main(scene_type=LiveScene, server=False) -> None:
    app = QApplication(sys.argv)
    icon = QIcon(get_icon_file())
    app.setWindowIcon(icon)
    communicate = Communicate()
    scene = scene_type(communicate)
    editor_window = EditorWidget(communicate, scene)
    preview_window = PreviewWidget(communicate, scene)
    preview_window.showFullScreen()
    editor_window.show()
    if AIWidget is not None:
        ai_window = AIWidget(communicate)
        ai_window.show()
    if server:
        from .server import ManimStudioServer
        server = ManimStudioServer(communicate)
        server.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(LiveScene)
