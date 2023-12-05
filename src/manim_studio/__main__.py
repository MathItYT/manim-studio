from manim_studio.live_scene import LiveScene
from manim_studio.communicate import Communicate
from manim_studio.editor_widget import EditorWidget
from manim_studio.preview_widget import PreviewWidget
from manim_studio.render_thread import RenderThread
from PyQt6.QtWidgets import QApplication
from .controls_widget import ControlsWidget
from manim import config
import sys


def main():
    config.disable_caching = True
    config.write_to_movie = False
    app = QApplication([])
    size = app.primaryScreen().size()
    size = (size.width(), size.height())
    communicate = Communicate()
    controls_widget = ControlsWidget()
    preview_widget = PreviewWidget(communicate, size)
    scene = LiveScene(communicate)
    editor_widget = EditorWidget(communicate, controls_widget, scene)
    render_thread = RenderThread(scene)
    preview_widget.show()
    editor_widget.show()
    render_thread.start()
    controls_widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
