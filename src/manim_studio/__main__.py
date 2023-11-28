from .main import main as run_manim_studio
from .live_scene import LiveScene
from .client.dialog import ClientDialog
from .client.client import ManimStudioClient
from PyQt6.QtWidgets import QApplication
from manim import logger, config, error_console
from rich.console import Console
import argparse
import sys


def import_module_from_file(file_name):
    from importlib import import_module
    import sys
    sys.path.append(".")
    module_name = file_name.replace(
        "/", ".").replace("\\", ".").replace(".py", "")
    return import_module(module_name)


def get_live_scene_classes_from_module(module):
    return [getattr(module, name)
            for name in dir(module)
            if name != "LiveScene"
            and isinstance(getattr(module, name), type)
            and issubclass(getattr(module, name), LiveScene)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", help="file to render",
                        default=None, required=False)
    parser.add_argument("--scene", "-s", help="scene to render",
                        default=None, required=False)
    parser.add_argument("--server", "-S", help="run server",
                        action="store_true", required=False)
    parser.add_argument("--connect", "-C", help="connect to server",
                        action="store_true", required=False)
    parser.add_argument("--resolution", "-r", help="resolution",
                        default=None, required=False)
    parser.add_argument("--background", "-b", help="background color",
                        default=None, required=False)
    parser.add_argument("--preview", "-p", help="preview the final result",
                        action="store_true", required=False)
    parser.add_argument("--transparent", "-t", help="transparent background",
                        action="store_true", required=False)
    parser.add_argument("--save_last_frame", "-l", help="save last frame",
                        action="store_true", required=False)
    parser.add_argument("--not_write", "-n", help="not write to any file",
                        action="store_true", required=False)
    args = parser.parse_args()
    preview = args.preview
    config.transparent = args.transparent
    if not args.not_write:
        config.save_last_frame = args.save_last_frame
        config.write_to_movie = not args.save_last_frame
    else:
        config.write_to_movie = False
        config.save_last_frame = False
    if args.connect:
        app = QApplication([])
        client_dialog = ClientDialog()
        client_dialog.exec()
        host, port, username, password = client_dialog.get_server_info()
        client = ManimStudioClient(host, port, username, password)
        client.show()
        if client.success:
            client.controls_dialog.show()
            sys.exit(app.exec())
    if args.resolution is not None:
        try:
            factor = config.frame_height / config.pixel_height
            width, height = args.resolution.split("x")
            config.pixel_width = int(width)
            config.pixel_height = int(height)
            config.frame_width = config.pixel_width * factor
            config.frame_height = config.pixel_height * factor
        except Exception:
            logger.error(
                "Invalid resolution format: It must be in the form WIDTHxHEIGHT")
            sys.exit(1)
    if args.background is not None:
        try:
            config.background_color = args.background
        except Exception:
            logger.error(
                "Invalid background color format: It must be in the form #RRGGBB")
            sys.exit(1)
    if args.file is None:
        run_manim_studio(LiveScene, args.server, preview=preview)
    else:
        module = import_module_from_file(args.file)
        live_scenes = get_live_scene_classes_from_module(module)
        if args.scene is None:
            if len(live_scenes) == 0:
                logger.error(
                    f"No live scene found in file {args.file}")
            elif len(live_scenes) == 1:
                run_manim_studio(
                    live_scenes[0], args.server, module, preview=preview)
            else:
                logger.info(
                    "More than one live scene found in file. Select one:")
                for i, live_scene in enumerate(live_scenes):
                    logger.info(f"{i+1}. {live_scene.__name__}")
                while True:
                    try:
                        i = int(input("Enter number: "))
                        if i < 1 or i > len(live_scenes):
                            raise ValueError()
                        break
                    except ValueError:
                        logger.info("Invalid input")
                run_manim_studio(
                    live_scenes[i-1], args.server, module, preview=preview)
        else:
            for live_scene in live_scenes:
                if live_scene.__name__ == args.scene:
                    run_manim_studio(live_scene, args.server,
                                     module, preview=preview)
                    break
            else:
                logger.error(
                    f"Live scene {args.scene} not found in file {args.file}")


if __name__ == "__main__":
    main()
