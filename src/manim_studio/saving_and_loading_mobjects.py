from manim import Mobject
import dill as pickle


def load_mobject(path: str) -> Mobject:
    with open(path, "rb") as f:
        return pickle.load(f)


def save_mobject(mobject: Mobject, path: str) -> None:
    globals()["console"] = None  # To fix a bug
    globals()["logger"] = None  # To fix a bug
    globals()["error_console"] = None  # To fix a bug
    self_ = globals()["self"]  # To fix a bug
    globals()["self"] = None  # To fix a bug
    with open(path, "wb") as f:
        pickle.dump(mobject, f)
    globals()["self"] = self_  # To fix a bug
