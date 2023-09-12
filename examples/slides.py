from manim_studio import *
from manim import *


class Slide(LiveScene):
    def construct(self):
        slides = [
            Text("Slide 1"),
            Text("Slide 2"),
            Text("Slide 3"),
            Text("Slide 4"),
            Text("Slide 5"),
        ]
        vg = VGroup(*slides)
        self.now_slide = vg[0]
        self.play(Write(self.now_slide))
        self.wait()

        for i in range(1, len(slides)):
            self.pause_slide()
            self.play(Transform(self.now_slide, vg[i]))

        super().construct()


if __name__ == "__main__":
    run_manim_studio(Slide)
