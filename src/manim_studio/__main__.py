from manim_studio.live_scene import LiveScene
from manim_studio.communicate import Communicate
from manim_studio.editor_widget import EditorWidget
from manim_studio.preview_widget import PreviewWidget
from manim_studio.render_thread import RenderThread
from PyQt6.QtWidgets import QApplication
from .controls_widget import ControlsWidget
from .inherits_dialog import InheritsDialog
from manim import config
import sys
import argparse
import importlib.util
from pathlib import Path


def import_from_file(file_name):
    file_name = Path(file_name)
    if file_name.suffix != ".py":
        raise ValueError("File name must end with .py")
    spec = importlib.util.spec_from_file_location(file_name, file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write_to_movie", "-w",
                        action="store_true", default=False)
    parser.add_argument("--file_name", "-f", type=str, default="none")
    parser.add_argument("--from_project", "-p", type=str, default="")
    args = parser.parse_args()
    if args.file_name != "none":
        module = import_from_file(args.file_name)
    else:
        module = None
    config.write_to_movie = args.write_to_movie
    config.write_to_movie = False
    app = QApplication([])
    size = app.primaryScreen().size()
    size = (size.width(), size.height())
    inherits_dialog = InheritsDialog(module, args.from_project)
    inherits_dialog.exec()
    communicate = Communicate()
    controls_widget = ControlsWidget()
    scene = inherits_dialog.get_scene(communicate)
    if scene is None:
        return
    editor_widget = EditorWidget(
        communicate, controls_widget, scene, args.from_project)
    render_thread = RenderThread(scene)
    preview_widget = PreviewWidget(communicate, size, render_thread)
    preview_widget.show()
    editor_widget.show()
    controls_widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
