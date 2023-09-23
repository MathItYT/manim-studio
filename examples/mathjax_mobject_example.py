from manim_studio import *
from manim import *
from time import sleep


class MathJaxExample(LiveScene):
    def construct(self):
        self.add_slider_command("x_times_1000", "0", "0", "10000", "10")
        sleep(1)  # Wait for the slider to be added to the scene

        current_x = 0.0

        def updater(mobject):
            nonlocal current_x
            if self.x_times_1000.get_value() / 1000 != current_x:
                current_x = self.x_times_1000.get_value() / 1000
                mobject.become(MathJax(f"x = {current_x:.2f}"))

        mathjax = MathJax("x = 0.00")
        mathjax.add_updater(updater)
        self.add(mathjax)

        super().construct()
