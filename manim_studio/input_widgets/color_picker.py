from PyQt6.QtWidgets import (
    QColorDialog,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QComboBox,
    QPlainTextEdit,
    QMessageBox
)
from PyQt6.QtGui import QColor

from manim import ManimColor, VMobject, Mobject

from ..api import ManimStudioAPI
from ..mobject_picker import MobjectPicker
from ..utils import make_snake_case


class ColorPicker(QGroupBox):
    def __init__(self, name: str, window_width: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.window_width = window_width
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel(f"{name}: RGBA(255, 255, 255, 255)")
        layout.addWidget(self.label)

        self.color_dialog = QColorDialog()
        self.color_dialog.currentColorChanged.connect(self.execute_expression)
        self.color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        self.color_dialog.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
        self.color_dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        layout.addWidget(self.color_dialog)

        expression_label = QLabel("Expression")
        layout.addWidget(expression_label)
        self.expression_selector = QComboBox()
        self.expression_selector.addItems([
            "Set Fill Color",
            "Set Stroke Color",
            "Custom Expression"
        ])
        self.expression_selector.setCurrentIndex(2)
        self.expression_selector.currentIndexChanged.connect(self.update_expression)
        self.expression_editor = QPlainTextEdit()
        self.expression_editor.setPlaceholderText("Enter a valid Python expression")
        layout.addWidget(self.expression_selector)
        layout.addWidget(self.expression_editor)
        self.color_dialog.currentColorChanged.connect(self.execute_expression)
        setattr(ManimStudioAPI.scene, make_snake_case(self.name), ManimColor((1.0, 1.0, 1.0)))
        setattr(ManimStudioAPI.scene, f"{make_snake_case(self.name)}_opacity", 1.0)
        self.color_dialog.setCurrentColor(QColor(255, 255, 255, 255))
    
    def execute_expression(self, color: QColor):
        self.label.setText(f"{self.name}: RGBA({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})")
        expression = self.expression_editor.toPlainText()
        if expression:
            value = f"ManimColor(({color.redF()}, {color.greenF()}, {color.blueF()}))"
            ManimStudioAPI.scene.code = f"""
self.{make_snake_case(self.name)} = {value}
self.{make_snake_case(self.name)}_opacity = {color.alphaF()}
{expression}
""".strip()
    
    def update_expression(self, index: int):
        if index == 2:
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
            self.expression_selector.setCurrentIndex(2)
            return
        mobject_name = mobject_name[0]
        if self.expression_selector.currentIndex() in range(2) and not isinstance(getattr(ManimStudioAPI.scene, mobject_name), VMobject):
            QMessageBox.warning(
                self,
                "Invalid Input",
                "The mobject's name must correspond to a VMobject with option"
                f"{self.expression_selector.currentText()}, "
                "the expression will not be updated"
            )
            self.expression_editor.setReadOnly(False)
            self.expression_selector.setCurrentIndex(2)
            return
        self.expression_editor.setReadOnly(True)
        if self.expression_selector.currentIndex() == 0:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".set_fill(color=self.{make_snake_case(self.name)}, "
                f"opacity=self.{make_snake_case(self.name)}_opacity)"
            )
        elif self.expression_selector.currentIndex() == 1:
            self.expression_editor.setPlainText(
                f"self.{mobject_name}"
                f".set_stroke(color=self.{make_snake_case(self.name)}, "
                f"opacity=self.{make_snake_case(self.name)}_opacity)"
            )
        self.execute_expression(self.color_dialog.currentColor())
