from .int_value_tracker import IntValueTracker


class BooleanValueTracker(IntValueTracker):
    def __init__(self, value=False, **kwargs):
        super().__init__(value=bool(value), **kwargs)

    def get_value(self) -> bool:
        return bool(super().get_value())

    def set_value(self, value: bool):
        return super().set_value(value)
