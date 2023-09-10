from PyQt6.QtWidgets import QApplication
import sys

from editor_widget import EditorWidget
from preview_widget import PreviewWidget
from live_scene import LiveScene
from communicate import Communicate


def main():
    app = QApplication(sys.argv)
    communicate = Communicate()
    scene = LiveScene(communicate)
    editor_window = EditorWidget(communicate, scene)
    preview_window = PreviewWidget(communicate, scene)
    preview_window.show()
    editor_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
