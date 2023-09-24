from manim import *
from manim_studio import *


class LoadMobjectExample(Scene):
    def construct(self):
        figure = load_mobject("mobjects_pkl/figure.pkl")
        self.play(FadeIn(figure))
