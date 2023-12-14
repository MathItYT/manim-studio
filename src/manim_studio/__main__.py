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
    spec = importlib.util.spec_from_file_location(file_name.stem, file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write_to_movie", "-w",
                        action="store_true", default=False)
    parser.add_argument("--file_name", "-f", type=str, default="none")
    parser.add_argument("--consider_manim_studio_time", "-c",
                        action="store_true", default=False)
    parser.add_argument("--resolution", "-r", type=str, default="1920x1080")
    parser.add_argument("--fps", "-fps", type=int, default=60)
    parser.add_argument("--include_secrets", "-s", action="store_true", default=False)
    args = parser.parse_args()
    if args.file_name != "none":
        module = import_from_file(args.file_name)
    else:
        module = None
    config.write_to_movie = args.write_to_movie
    config.frame_rate = args.fps
    config.disable_caching = True
    width, height = args.resolution.split("x")
    config.pixel_width, config.pixel_height = int(width), int(height)
    max_dimension = max(config.pixel_width, config.pixel_height)
    if max_dimension == config.pixel_width:
        config.frame_width = int(config.pixel_width / config.pixel_height * 8)
        config.frame_height = 8
    else:
        config.frame_height = int(config.pixel_height / config.pixel_width * 8)
        config.frame_width = 8
    app = QApplication([])
    size = app.primaryScreen().size()
    size = (size.width(), size.height())
    inherits_dialog = InheritsDialog(
        module, args.consider_manim_studio_time, args.include_secrets)
    inherits_dialog.exec()
    communicate = Communicate()
    controls_widget = ControlsWidget()
    scene = inherits_dialog.get_scene(communicate)
    if scene is None:
        return
    editor_widget = EditorWidget(
        communicate, controls_widget, scene)
    render_thread = RenderThread(scene)
    preview_widget = PreviewWidget(communicate, size, render_thread)
    render_thread.start()
    preview_widget.show()
    editor_widget.show()
    controls_widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
