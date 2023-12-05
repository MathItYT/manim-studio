from manim import Dot


class DotTracker(Dot):
    def __repr__(self) -> str:
        return f"DotTracker(np.array([{self.get_center()[0]}, {self.get_center()[1]}, {self.get_center()[2]}]))"
