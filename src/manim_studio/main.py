from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys

from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .live_scene import LiveScene
from .communicate import Communicate
from .ai_widget import AIWidget
from .get_icon_file import get_icon_file
from .inherits_dialog import InheritsDialog


def main(scene_type=LiveScene, server=False, namespace=None, preview=False) -> None:
    """
    Run the main window of Manim Studio.

    Parameters
    ----------
    scene_type
        The base class of the scene to be rendered.
    server
        Whether to run the server.
    namespace
        The namespace of the scene to be rendered.
    preview
        Whether to preview the final result.
    """
    app = QApplication(sys.argv)
    screen_size = app.primaryScreen().size()
    w, h = screen_size.width(), screen_size.height()
    icon = QIcon(get_icon_file())
    app.setWindowIcon(icon)
    inherits_dialog = InheritsDialog(scene_type, namespace)
    inherits_dialog.exec()
    scene_type = inherits_dialog.set_scene_type_base_classes()
    communicate = Communicate()
    scene = scene_type(communicate, namespace)
    editor_window = EditorWidget(communicate, scene, server)
    preview_window = PreviewWidget(communicate, scene, (w, h), preview)
    scene.set_editor(editor_window)
    preview_window.show()
    editor_window.show()
    if AIWidget is not None:
        ai_window = AIWidget(communicate)
        ai_window.show()
    if server:
        from .server import ManimStudioServer
        server_window = ManimStudioServer(communicate, editor_window)
        server_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(LiveScene)
