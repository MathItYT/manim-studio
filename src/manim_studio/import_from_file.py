from pathlib import Path
import importlib.util


def import_from_file(file_name):
    file_name = Path(file_name)
    if file_name.suffix != ".py":
        raise ValueError("File name must end with .py")
    spec = importlib.util.spec_from_file_location(file_name.stem, file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module