from manim import *
from manim_studio import *


class LoadSnippetExample(Scene):
    def construct(self):
        load_snippet(self, "snippets/scene1.mss")
        self.play(self.x_times_1000.animate.set_value(1000))
