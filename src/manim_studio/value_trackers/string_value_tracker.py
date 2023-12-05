from manim import ValueTracker, Mobject


class StringValueTracker(ValueTracker):
    def __init__(self, value: str = ""):
        Mobject.__init__(self)
        self.value = value

    def get_value(self) -> str:
        return self.value

    def set_value(self, value: str) -> None:
        self.value = str(value)

    def increment_value(self, d_value: float):
        pass

    def __repr__(self) -> str:
        return f"StringValueTracker({self.get_value().__repr__()})"
