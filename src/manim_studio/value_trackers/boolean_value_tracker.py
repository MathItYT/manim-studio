from manim import ValueTracker, Mobject


class BooleanValueTracker(ValueTracker, Mobject):
    def __init__(self, value: bool = False):
        Mobject.__init__(self)
        self.set_value(value)

    def get_value(self) -> bool:
        return bool(self.value)

    def set_value(self, value: bool):
        self.value = value
        return self

    def increment_value(self, d_value: float):
        pass

    def __repr__(self) -> str:
        return f"BooleanValueTracker({self.get_value()})"
