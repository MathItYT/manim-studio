from manim import ValueTracker, Mobject


class StringValueTracker(ValueTracker):
    """A value tracker for string values."""

    def __init__(self, value="", **kwargs):
        Mobject.__init__(self, **kwargs)
        self.set_value(value)

    def get_value(self) -> str:
        return str(self.value)

    def set_value(self, value: str):
        self.value = str(value)
