from PyQt6.QtWidgets import (
    QSlider,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QComboBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from manim import Mobject, VMobject

from ..api import ManimStudioAPI
from ..mobject_picker import MobjectPicker
from ..utils import make_snake_case


class DoubleSlider(QSlider):
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals: int = 3, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super().value())/self._multi
        self.doubleValueChanged.emit(value)

    def value(self) -> float:
        return float(super().value()) / self._multi

    def setMinimum(self, value: float):
        return super().setMinimum(int(value * self._multi))

    def setMaximum(self, value: float):
        return super().setMaximum(int(value * self._multi))

    def setSingleStep(self, value: float):
        return super().setSingleStep(int(value * self._multi))

    def singleStep(self) -> float:
        return float(super().singleStep()) / self._multi

    def setValue(self, value: float):
        super().setValue(int(value * self._multi))


class RangeSlider(QGroupBox):
    def __init__(
        self,
        name: str,
        value: float,
        min_val: float,
        max_val: float,
        single_step: float,
        window_width: int,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.window_width = window_width

        step = single_step
        decimals = 0
        while step < 1:
            step *= 10
            decimals += 1

        self.slider = DoubleSlider(decimals=decimals)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        
        self.min_label = QLabel(str(min_val))
        self.max_label = QLabel(str(max_val))
        self.min_val = min_val
        self.max_val = max_val

        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setSingleStep(single_step)
        self.slider.setValue(value)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel(f"{name}: {value}")
        layout.addWidget(self.label)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.min_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.max_label)
        layout.addLayout(slider_layout)

        expression_label = QLabel("Expression")
        layout.addWidget(expression_label)
        self.expression_selector = QComboBox()
        self.expression_selector.addItems([
            "Set Stroke Width",
            "Set Fill Opacity",
            "Set Stroke Opacity",
            "Set Height",
            "Set Width",
            "Custom Expression"
        ])
        self.expression_selector.setCurrentIndex(5)
        self.expression_selector.currentIndexChanged.connect(self.update_expression)
        self.expression_editor = QPlainTextEdit()
        self.expression_editor.setPlaceholderText("Enter a valid Python expression")
        layout.addWidget(self.expression_selector)
        layout.addWidget(self.expression_editor)
        self.slider.doubleValueChanged.connect(self.execute_expression)

    def execute_expression(self, value: float):
        self.label.setText(f"{self.name}: {value}")
        expression = self.expression_editor.toPlainText()
        ManimStudioAPI.scene.code = f"""
self.{make_snake_case(self.name)} = {value}
{expression}
""".strip()
    
    def update_expression(self):
        if self.expression_selector.currentIndex() == 5:
            self.expression_editor.setReadOnly(False)
            return
        self.expression_editor.setReadOnly(True)
        mobject_name = MobjectPicker(
            self.window_width,
            ManimStudioAPI.scene.camera,
            Mobject
        ).wait_for_selection()
        if mobject_name is None:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "You must enter a valid mobject's name, "
                "the expression will not be updated"
            )
            self.expression_editor.setReadOnly(False)
            self.expression_selector.setCurrentIndex(5)
            return
        mobject_name = mobject_name[0]
        if self.expression_selector.currentIndex() in range(3) and not isinstance(getattr(ManimStudioAPI.scene, mobject_name), VMobject):
            QMessageBox.warning(
                self,
                "Invalid Input",
                "The mobject's name must correspond to a VMobject with option"
                f"{self.expression_selector.currentText()}, "
                "the expression will not be updated"
            )
            self.expression_editor.setReadOnly(False)
            self.expression_selector.setCurrentIndex(5)
            return
        self.expression_editor.setReadOnly(True)
        if self.expression_selector.currentIndex() == 0:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".set_stroke(width=self.{make_snake_case(self.name)})"
            )
        elif self.expression_selector.currentIndex() == 1:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".set_fill(opacity=self.{make_snake_case(self.name)})"
            )
        elif self.expression_selector.currentIndex() == 2:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".set_stroke(opacity=self.{make_snake_case(self.name)})"
            )
        elif self.expression_selector.currentIndex() == 3:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".scale_to_fit_height(self.{make_snake_case(self.name)})"
            )
        elif self.expression_selector.currentIndex() == 4:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".scale_to_fit_width(self.{make_snake_case(self.name)})"
            )
        self.execute_expression(self.slider.value())
