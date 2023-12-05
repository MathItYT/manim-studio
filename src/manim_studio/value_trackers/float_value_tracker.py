from manim import ValueTracker


class FloatValueTracker(ValueTracker):
    def __repr__(self) -> str:
        return f"FloatValueTracker({self.get_value()})"
