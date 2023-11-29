from manim import Mobject
import dill as pickle


def load_mobject(path: str) -> Mobject:
    with open(path, "rb") as f:
        return pickle.load(f)


def save_mobject(mobject: Mobject, path: str) -> None:
    with open(path, "wb") as f:
        pickle.dump(mobject, f)
