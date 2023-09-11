from PyQt6.QtWidgets import QApplication
import sys

from editor_widget import EditorWidget
from preview_widget import PreviewWidget
from live_scene import LiveScene
from communicate import Communicate


def main(scene_type: type[LiveScene]):
    app = QApplication(sys.argv)
    communicate = Communicate()
    scene = scene_type(communicate)
    editor_window = EditorWidget(communicate, scene)
    preview_window = PreviewWidget(communicate, scene)
    preview_window.showMaximized()
    editor_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(LiveScene)
