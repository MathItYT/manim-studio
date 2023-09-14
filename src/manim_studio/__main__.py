from .main import main as run_manim_studio
from .live_scene import LiveScene
from manim import logger
import argparse


def get_live_scene_classes_from_file(file_name):
    from importlib import import_module
    module_name = file_name.replace(
        "/", ".").replace("\\", ".").replace(".py", "")
    module = import_module(module_name)
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
    args = parser.parse_args()
    if args.file is None:
        run_manim_studio(LiveScene)
    else:
        live_scenes = get_live_scene_classes_from_file(args.file)
        if args.scene is None:
            if len(live_scenes) == 0:
                logger.error(
                    f"No live scene found in file {args.file}")
            elif len(live_scenes) == 1:
                run_manim_studio(live_scenes[0])
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
                run_manim_studio(live_scenes[i-1])
        else:
            for live_scene in live_scenes:
                if live_scene.__name__ == args.scene:
                    run_manim_studio(live_scene)
                    break
            else:
                logger.error(
                    f"Live scene {args.scene} not found in file {args.file}")


if __name__ == "__main__":
    main()
