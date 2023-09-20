from manim_studio import *
from manim import *
from time import sleep


class MathJaxExample(LiveScene):
    def construct(self):
        self.add_slider_command("x_times_1000", "0", "0", "10000", "1000")
        sleep(1)  # Wait for the slider to be added to the scene

        def updater(mobject):
            mobject.set_expr(
                f"x = {int(self.x_times_1000.get_value() / 1000)}")

        mathjax = MathJax("x = 0")
        mathjax.add_updater(updater)
        self.add(mathjax)

        super().construct()
