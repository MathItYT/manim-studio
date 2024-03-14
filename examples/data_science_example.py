from manim import *
from manim_studio import hold_on
import random


def noise(k: int, noise_factor: float = 0.5):
   return k+((random.random()*2)-1)*noise_factor


class DataScienceExample(Scene):
    def construct(self):
        self.plane = NumberPlane(
            x_range=[-10, 10, 1],
            y_range=[-10, 10, 1],
            x_length=6,
            y_length=6,
            background_line_style={"stroke_opacity": 0.5, "stroke_color": TEAL}
        )
        labels = self.plane.get_axis_labels("X", "Y")
        self.play(Create(self.plane), DrawBorderThenFill(labels))
        self.n = 100
        self.noise_factor = 0.5
        self.generate_points(100, first_time=True)

        hold_on(self, locals())
    
    def generate_points(self, n: int, noise_factor: float = 0.5, first_time: bool = False):
        f = np.vectorize(lambda k: noise(k, noise_factor))
        x = f(np.linspace(-10, 10, n))
        y = f(np.linspace(-10, 10, n))
        points = VGroup(*[Dot(self.plane.coords_to_point(i, j)) for i, j in zip(x, y)])
        points.shuffle()
        if first_time:
            self.play(LaggedStartMap(lambda m: FadeIn(m, scale=0.5), points, run_time=1))
        else:
            self.remove(*self.points)
            self.add(points)
        self.points = points
    
    def setup_deepness(self):
        self.deepness = 0
