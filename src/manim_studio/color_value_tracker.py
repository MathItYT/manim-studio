from manim import ValueTracker, Mobject
from colour import Color
import numpy as np


class ColorValueTracker(ValueTracker):
    def __init__(self, value=np.array([0, 0, 0, 1]), **kwargs):
        Mobject.__init__(self, **kwargs)
        self.set_points(np.zeros((1, 4)))
        self.set_value(value)

    def get_value(self) -> Color:
        return Color(rgb=np.array(self.points[0, :3])).hex, self.points[0, 3]

    def set_value(self, value: np.ndarray):
        self.points[0, :4] = np.array(value)
        return self
