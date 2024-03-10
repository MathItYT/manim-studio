import importlib
from types import ModuleType
from pathlib import Path

from manim import Scene


def import_from_file(path_to_file: Path) -> ModuleType:
    """Import a module from a file."""
    spec = importlib.util.spec_from_file_location(path_to_file.stem, path_to_file)
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
    
