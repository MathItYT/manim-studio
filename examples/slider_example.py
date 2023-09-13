from manim_studio import *
from manim import *


class SliderExample(LiveScene):
    def construct(self):
        self.add_slider_command(
            "a", "1", "-10", "10", "1")
        self.add_slider_command(
            "b", "1", "-10", "10", "1")
        self.add_slider_command(
            "c", "1", "-10", "10", "1")
        plane = NumberPlane()
        self.play(Write(plane))
        self.wait()

        def update_quadratic(m):
            m.become(plane.plot(lambda x: self.a.get_value() * x *
                     x + self.b.get_value() * x + self.c.get_value(), color=YELLOW))

        plane_graph = VMobject().add_updater(update_quadratic)
        self.add(plane_graph)

        super().construct()


if __name__ == "__main__":
    run_manim_studio(SliderExample)
