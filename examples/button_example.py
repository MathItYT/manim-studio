from manim_studio import *
from manim import *


class ButtonExample(LiveScene):
    def construct(self):
        self.current_code = "circle = Circle()\nself.play(Create(circle))"
        self.run_instruction()
        self.add_button_command(
            "Indicate Circle", "self.play(Indicate(circle))")
        super().construct()
