from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QGridLayout,
    QWidget,
    QLabel,
    QDialog,
    QComboBox,
    QPushButton,
    QDoubleSpinBox,
    QHBoxLayout
)
from PyQt6.QtGui import QMovie
from manim import (
    Mobject,
    VMobject
)
import importlib
from pathlib import Path
import sys


def get_animation_path(animation_name: str):
    manim_studio = importlib.import_module("manim_studio")
    manim_studio_path = Path(manim_studio.__file__).parent
    return str(manim_studio_path / "assets" / f"{animation_name}.gif")


class AnimationWidget(QGroupBox):
    def __init__(self, animation_picker, animation_name):
        super().__init__()
        self.animation_picker = animation_picker
        self.animation_name = animation_name
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.animation_label = QLabel()
        self.animation_label.setFixedSize(int(16 / 9 * 200), 200)
        self.animation_label.setStyleSheet("background-color: black;")
        self.animation_label.setMovie(
            QMovie(get_animation_path(self.animation_name)))
        self.animation_label.movie().setScaledSize(
            self.animation_label.size())
        self.layout().addWidget(self.animation_label)
        self.name_label = QLabel(self.animation_name)
        self.layout().addWidget(self.name_label)
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(
            self.animation_label.movie().start)
        self.layout().addWidget(self.preview_button)
        self.stop_button = QPushButton("Stop Preview")
        self.stop_button.clicked.connect(
            self.animation_label.movie().stop)
        self.layout().addWidget(self.stop_button)
        self.animation_label.mouseDoubleClickEvent = self.play_animation

    def play_animation(self, event):
        dialog = QDialog()
        dialog.setGeometry(0, 0, 400, 200)
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.layout().setSpacing(0)
        dialog.setModal(True)
        dialog.setWindowTitle("Select mobject to animate (they must be attributes of the scene)" if self.animation_name !=
                              "ReplacementTransform" else "Select mobjects to animate (they must be attributes of the scene)")
        dialog.combo_box = QComboBox()
        dialog.combo_box.addItems(
            [mob for mob in dir(self.animation_picker.editor.scene) if isinstance(getattr(self.animation_picker.editor.scene, mob), self.get_animation_mobject_type())])
        dialog.layout().addWidget(dialog.combo_box)
        if self.animation_name == "ReplacementTransform":
            dialog.combo_box_2 = QComboBox()
            dialog.combo_box_2.addItems(
                [mob for mob in dir(self.animation_picker.editor.scene) if isinstance(getattr(self.animation_picker.editor.scene, mob), self.get_animation_mobject_type())])
            dialog.layout().addWidget(dialog.combo_box_2)
        if self.animation_name == "ScaleInPlace":
            dialog.scale_factor_label = QLabel("Scale Factor:")
            dialog.layout().addWidget(dialog.scale_factor_label)
            dialog.scale_factor = QDoubleSpinBox()
            dialog.scale_factor.setRange(-sys.float_info.max,
                                         sys.float_info.max)
            dialog.scale_factor.setValue(2)
            dialog.layout().addWidget(dialog.scale_factor)
        if self.animation_name == "animated_move_to":
            dialog.position_group_box = QGroupBox()
            dialog.position_group_box.setLayout(
                QHBoxLayout(dialog.position_group_box))
            dialog.position_group_box.layout().setContentsMargins(0, 0, 0, 0)
            dialog.position_group_box.layout().setSpacing(0)
            dialog.position_group_box.layout().addWidget(QLabel("Position:"))
            dialog.x_spin_box = QDoubleSpinBox()
            dialog.x_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
            dialog.x_spin_box.setValue(0)
            dialog.position_group_box.layout().addWidget(dialog.x_spin_box)
            dialog.y_spin_box = QDoubleSpinBox()
            dialog.y_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
            dialog.y_spin_box.setValue(0)
            dialog.position_group_box.layout().addWidget(dialog.y_spin_box)
            dialog.z_spin_box = QDoubleSpinBox()
            dialog.z_spin_box.setRange(-sys.float_info.max, sys.float_info.max)
            dialog.z_spin_box.setValue(0)
            dialog.position_group_box.layout().addWidget(dialog.z_spin_box)
            dialog.layout().addWidget(dialog.position_group_box)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.accept)
        dialog.layout().addWidget(dialog.ok_button)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Rejected:
            return
        if dialog.combo_box.currentText() == "":
            return
        if self.animation_name in ("Transform", "ReplacementTransform"):
            if dialog.combo_box_2.currentText() == "":
                return
            self.animation_picker.editor.communicate.update_scene.emit(
                f"self.play({self.animation_name}(getattr(self, {dialog.combo_box.currentText().__repr__()}), getattr(self, {dialog.combo_box_2.currentText().__repr__()})))")
        elif self.animation_name == "animated_move_to":
            self.animation_picker.editor.communicate.update_scene.emit(
                f"self.play(getattr(self, {dialog.combo_box.currentText().__repr__()}).animate.move_to(np.array([{dialog.x_spin_box.value()}, {dialog.y_spin_box.value()}, {dialog.z_spin_box.value()}])))")
        elif self.animation_name == "ScaleInPlace":
            self.animation_picker.editor.communicate.update_scene.emit(
                f"self.play(ScaleInPlace(getattr(self, {dialog.combo_box.currentText().__repr__()}), {dialog.scale_factor.value()}))")
        else:
            self.animation_picker.editor.communicate.update_scene.emit(
                f"self.play({self.animation_name}(getattr(self, {dialog.combo_box.currentText().__repr__()})))")

    def get_animation_mobject_type(self):
        if self.animation_name in ("ReplacementTransform", "Create", "Write", "DrawBorderThenFill"):
            return VMobject
        return Mobject


class AnimationPicker(QScrollArea):
    def __init__(self, editor):
        super().__init__()
        self.setWindowTitle("Animation Picker")
        self.editor = editor
        self.init_supported_animations()
        self.init_ui()

    def init_supported_animations(self):
        self.supported_animations = [
            "Create",
            "FadeIn",
            "Write",
            "DrawBorderThenFill",
            "FadeOut",
            "ReplacementTransform",
            "ScaleInPlace",
            "GrowFromCenter",
            "animated_move_to"
        ]

    def init_ui(self):
        self.setGeometry(0, 0, int(16 / 9 * 200) * 3, 200 * 3)
        self.setWidgetResizable(True)
        self.setWidget(QWidget())
        self.widget().setLayout(QVBoxLayout(self.widget()))
        self.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.widget().layout().setSpacing(0)
        self.animation_group_box = QGroupBox("Animations")
        self.widget().layout().addWidget(self.animation_group_box)
        self.animation_group_box.setLayout(
            QGridLayout(self.animation_group_box))
        self.animation_group_box.layout().setContentsMargins(0, 0, 0, 0)
        self.animation_group_box.layout().setSpacing(0)
        for i, animation in enumerate(self.supported_animations):
            self.animation_group_box.layout().addWidget(
                AnimationWidget(self, animation), i // 3, i % 3)
