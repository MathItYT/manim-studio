from manim import ValueTracker


class BytesValueTracker(ValueTracker):
    def __init__(
        self,
        value: bytes = b"",
        *args,
        **kwargs,
    ):
        super().__init__(value, *args, **kwargs)
        self.value = value

    def get_value(self) -> bytes:
        return self.value

    def set_value(self, value: bytes):
        self.value = value
