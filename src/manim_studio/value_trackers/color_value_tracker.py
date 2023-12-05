from manim import ValueTracker, VMobject, rgb_to_color, color_to_rgba
import numpy as np


class ColorValueTracker(ValueTracker, VMobject):
    def __init__(self, color: np.ndarray = np.array([0, 0, 0, 1])):
        VMobject.__init__(self)
        self.set_value(color)

    def get_value(self) -> np.ndarray:
        return self.get_color(), self.get_fill_opacity()

    def set_value(self, value: np.ndarray):
        self.set_fill(color=rgb_to_color((value[:3])), opacity=value[3])
        return self

    def __repr__(self) -> str:
        color = color_to_rgba(*self.get_value())
        return f"ColorValueTracker(np.array([{color[0]}, {color[1]}, {color[2]}, {color[3]}]))"
