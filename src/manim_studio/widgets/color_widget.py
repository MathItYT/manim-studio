from PyQt6.QtWidgets import QColorDialog
import numpy as np

from manim_studio.value_trackers.color_value_tracker import ColorValueTracker


class ColorWidget(QColorDialog):
    """A color picker to edit a color property."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        self.color_tracker = ColorValueTracker(np.array([0, 0, 0, 255]))
        self.currentColorChanged.connect(lambda qcolor: self.color_tracker.set_value(
            np.array([qcolor.red() / 255, qcolor.green() / 255, qcolor.blue() / 255, qcolor.alpha() / 255])))
        self.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
