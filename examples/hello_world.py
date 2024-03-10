from manim import *
from manim_studio import hold_on


class ExampleScene(Scene):
    def construct(self):
        self.play(Write(Text("Hello, World!")))
        hold_on(self)
