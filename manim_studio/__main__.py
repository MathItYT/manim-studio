import argparse
from pathlib import Path
from types import ModuleType
from threading import Thread

from PyQt6.QtWidgets import QApplication

from manim import Scene
from manim._config import config

from .api import ManimStudioAPI
from .utils import import_module_by_name_or_path, import_from_file
from .window import Window


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="The file to open")
    parser.add_argument("--scene", help="The scene to open")
    parser.add_argument("--plugins", nargs="*", help="The plugins to load")
    parser.add_argument(
        "--consider_studio_time",
        action="store_true",
        help="Whether to consider Manim Studio time"
    )
    args = parser.parse_args()

    if args.scene and not args.file:
        raise ValueError(
            "You must provide a file when providing a scene to use.")

    if args.consider_studio_time:
        ManimStudioAPI.consider_studio_time = True

    path_to_file = Path(args.file) if args.file else None

    module = import_from_file(path_to_file) if path_to_file else None

    scene_class: type[Scene] = getattr(module, args.scene) if module else Scene
    plugins = args.plugins or []
    plugins: list[ModuleType] = [
        import_module_by_name_or_path(plugin)
        for plugin in plugins
    ]
    config.write_to_movie = False

    ManimStudioAPI.enabled = True
    scene = scene_class()
    scene.code = None
    path_to_file = str(path_to_file) if path_to_file else None
    ManimStudioAPI(scene, module, path_to_file, plugins)
    scene.setup_deepness()
    thread = Thread(target=scene.render, daemon=True)
    thread.start()

    app = QApplication([])
    screen = app.primaryScreen()
    window_size = screen.size()
    window_size_as_tuple = (window_size.width(), window_size.height())
    window = Window(
        window_size_as_tuple,
        ManimStudioAPI.scene
    )
    window.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
