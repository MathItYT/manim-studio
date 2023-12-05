from manim import ValueTracker


class IntValueTracker(ValueTracker):
    def __init__(self, value: int = 0):
        super().__init__(value)

    def get_value(self) -> float:
        return int(super().get_value())

    def __repr__(self) -> str:
        return f"IntValueTracker({self.get_value()})"
