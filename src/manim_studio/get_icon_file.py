def get_icon_file():
    import importlib
    from pathlib import Path

    module = importlib.import_module("manim_studio")
    module_path = Path(module.__file__).parent
    icon_folder = module_path / "assets"
    icon_file = icon_folder / "favicon.ico"
    return str(icon_file.absolute())
