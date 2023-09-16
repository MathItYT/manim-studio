from manim_studio import *
import numpy as np


class Example(LiveScene):
    def construct(self):
        self.add_dropdown_command(
            "stroke_width", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], "4")
        self.add_color_widget_command("stroke", np.array([255, 0, 0, 255]))
        self.add_color_widget_command("fill", np.array([255, 0, 0, 0]))
        self.add_slider_command("radius_times_1000", "1000", "1", "14000", "1")

        super().construct()
