from manim import *


class ManimStudio(Scene):
    def construct(self):
        banner = ManimBanner()
        studio = Tex("Studio")
        studio.scale(4)

        vg = VGroup(banner, studio).arrange(RIGHT, buff=0.5)
        studio.set_y(banner.M.get_bottom()[1] + studio.get_height() / 2)
        self.add(vg)
