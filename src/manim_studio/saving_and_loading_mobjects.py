from manim import Mobject
import dill as pickle


def load_mobject(path: str) -> Mobject:
    with open(path, "rb") as f:
        return pickle.load(f)


def save_mobject(mobject: Mobject, path: str, scope=None) -> None:
    scope["console"] = None  # To fix a bug
    scope["logger"] = None  # To fix a bug
    scope["error_console"] = None  # To fix a bug
    self_ = scope["self"]  # To fix a bug
    scope["self"] = None  # To fix a bug
    with open(path, "wb") as f:
        pickle.dump(mobject, f)
    scope["self"] = self_  # To fix a bug
