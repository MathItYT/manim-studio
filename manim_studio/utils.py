import importlib
from types import ModuleType
from pathlib import Path
import string

from manim import Scene


def import_module_by_name_or_path(name_or_path: str) -> ModuleType:
    """Import a module by name or path."""
    if name_or_path.endswith(".py"):
        return import_from_file(Path(name_or_path))
    return importlib.import_module(name_or_path)


def import_from_file(path_to_file: Path) -> ModuleType:
    """Import a module from a file."""
    spec = importlib.util.spec_from_file_location(
        path_to_file.stem, path_to_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def qt_coords_to_manim_coords(
    scene: Scene,
    x: float,
    y: float,
    label_x: int,
    label_y: int,
    label_width: int,
    label_height: int
) -> tuple[float, float]:
    """Convert pixel coordinates to Manim coordinates."""
    x -= label_x
    y -= label_y
    x /= label_width
    y /= label_height
    x *= scene.camera.frame_width
    y *= scene.camera.frame_height
    x -= scene.camera.frame_width / 2
    y -= scene.camera.frame_height / 2
    y *= -1
    return x, y


def make_snake_case(name: str) -> str:
    name = name.lstrip(string.digits + string.punctuation + string.whitespace)
    name = name.rstrip(string.punctuation + string.whitespace)
    name = name.split()
    name = "_".join(name)
    name = name.lower()
    return name


def make_camel_case(text: str, default: str) -> str:
    text = text.lstrip(string.punctuation + string.whitespace + string.digits)
    text = text.rstrip(string.punctuation + string.whitespace)
    if text == "":
        return default
    text = text.split()
    text = "".join(word.capitalize() for word in text)
    return text
