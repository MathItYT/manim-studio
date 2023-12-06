from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QMessageBox
import inspect
from PyQt6.QtGui import QValidator
from manim import *
from .live_scene import LiveScene
from .communicate import Communicate
import manim


class PythonicValidator(QValidator):
    def validate(self, string: str, pos: int):
        if string == "":
            return (QValidator.State.Acceptable, string, pos)
        try:
            eval(string, {string: None})
        except Exception as e:
            return (QValidator.State.Invalid, string, pos)
        return (QValidator.State.Acceptable, string, pos)


class InheritsDialog(QDialog):
    def __init__(self, module, project_path: str):
        super().__init__()
        self.setWindowTitle("Choose your kinds of scenes")
        self.setLayout(QVBoxLayout())
        self.setModal(True)
        self.module = module or manim
        self.project_path = project_path
        self.initUI()

    def initUI(self):
        if self.project_path:
            label = QLabel(f"You are loading from a project file in {
                           self.project_path}")
            self.layout().addWidget(label)
            self.ok_button = QPushButton("OK")
            self.ok_button.clicked.connect(self.accept)
            self.layout().addWidget(self.ok_button)
            return
        welcome_label = QLabel("Welcome to Manim Studio!")
        self.layout().addWidget(welcome_label)
        self.scene_types = [scene_type for _, scene_type in inspect.getmembers(
            self.module, inspect.isclass) if issubclass(scene_type, Scene) and scene_type not in (Scene, LiveScene)]
        choose_label = QLabel("Choose your kinds of scenes:")
        self.layout().addWidget(choose_label)
        self.checkboxes: list[QCheckBox] = []
        for scene_type in self.scene_types:
            checkbox = QCheckBox(scene_type.__name__)
            self.layout().addWidget(checkbox)
            self.checkboxes.append(checkbox)
        self.layout().addWidget(QLabel("Choose the name of your scene:"))
        self.scene_name = QLineEdit()
        self.scene_name.setText("MyScene")
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout().addWidget(self.scene_name)
        self.layout().addWidget(self.ok_button)
        self.scene_name.setValidator(PythonicValidator())

    def get_scene(self, communicate: Communicate):
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        if self.project_path:
            with open(self.project_path) as f:
                codes = f.read().split("\n---\n")
            bases = codes[0].split(",")
            bases = [eval(base) for base in bases]
            class_name = codes[1]
            return type(class_name, tuple(bases), {"communicate": communicate})(communicate=communicate, mro_without_live_scene=bases, project=self.project_path)
        if not self.scene_name.text():
            QMessageBox.critical(
                self, "Error", "You must choose a name for your scene")
            return None
        mro = []
        for checkbox, scene_type in zip(self.checkboxes, self.scene_types):
            if checkbox.isChecked():
                mro.append(scene_type)
        right_mro = []
        for scene_type in mro:
            if any(issubclass(other_scene_type, scene_type) for other_scene_type in mro if other_scene_type is not scene_type) or scene_type in right_mro:
                continue
            right_mro.append(scene_type)
        if not any(issubclass(scene_type, LiveScene) for scene_type in mro):
            right_mro.insert(0, LiveScene)
        mro = right_mro.copy()
        mro_without_live_scene = [scene_type for scene_type in mro if not issubclass(
            scene_type, LiveScene)] or [Scene]
        return type(self.scene_name.text(), tuple(mro), {"communicate": communicate})(communicate=communicate, mro_without_live_scene=mro_without_live_scene)
