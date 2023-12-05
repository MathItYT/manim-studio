from manim import ValueTracker, Mobject


class ListValueTracker(ValueTracker):
    def __init__(self, value: list = []):
        Mobject.__init__(self)
        self.value = value

    def get_value(self) -> list:
        return self.value

    def set_value(self, value: list) -> None:
        self.value = list(value)

    def increment_value(self, d_value: float):
        pass

    def __repr__(self) -> str:
        return f"ListValueTracker({self.get_value().__repr__()})"
