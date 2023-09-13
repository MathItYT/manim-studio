from manim_studio import *
from manim import *
from time import sleep


class ColorWidgetExample(LiveScene):
    def construct(self):
        self.add_color_widget_command("fill_color", np.array([0, 0, 0, 255]))
        sleep(1)  # wait for the color widget to be created

        def updater(circle):
            fill_color, opacity = self.fill_color.get_value()
            circle.become(Circle(stroke_color=WHITE).set_fill(
                fill_color, opacity=opacity))

        self.circle = VMobject().add_updater(updater)
        self.add(self.circle)

        super().construct()


if __name__ == "__main__":
    run_manim_studio(ColorWidgetExample)
