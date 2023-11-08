from manim import ValueTracker


class IntValueTracker(ValueTracker):
    def get_value(self) -> int:
        return int(self.points[0, 0])

    def set_value(self, value: int):
        self.points[0, 0] = int(value)
        return self
