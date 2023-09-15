from manim_studio import *
from manim import *
from time import sleep


class CheckboxWidgetExample(LiveScene):
    def construct(self):
        self.add_checkbox_command("dark_theme", True)
        sleep(1)  # wait for the checkbox widget to be created

        def updater(circle):
            if self.dark_theme.get_value():
                circle.become(Circle().set_color(WHITE))
                self.camera.background_color = BLACK
            else:
                circle.become(Circle().set_color(BLACK))
                self.camera.background_color = WHITE

        circ = VMobject().add_updater(updater)
        self.add(circ)

        super().construct()
