from manim import ValueTracker, Mobject, ManimColor
import numpy as np


class ColorValueTracker(ValueTracker):
    """A value tracker for color. It contains an array of 3 values and an alpha value."""

    def __init__(self, value=np.array([0, 0, 0, 1]), **kwargs):
        Mobject.__init__(self, **kwargs)
        self.set_points(np.zeros((1, 4)))
        self.set_value(value)

    def get_value(self) -> ManimColor:
        return ManimColor.from_rgba(self.points[0, :4]).to_hex(), self.points[0, 3]

    def set_value(self, value: np.ndarray):
        self.points[0, :4] = np.array(value)
        return self
