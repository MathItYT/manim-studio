from manim import *
from manim_studio import hold_on


class ExampleScene(Scene):
    def construct(self):
        self.text = Text("Hello, World!")
        self.play(Write(self.text))
        hold_on(self, locals())
    
    def setup_deepness(self):
        self.deepness = 0
