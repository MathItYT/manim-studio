from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QMessageBox
import inspect
from PyQt6.QtGui import QValidator
from manim import Scene
from .live_scene import LiveScene
from .communicate import Communicate
import manim


class PythonicValidator(QValidator):
    def validate(self, string: str, pos: int):
        if string == "":
            return (QValidator.State.Acceptable, string, pos)
        try:
            eval(string, {string: None})
        except SyntaxError:
            return (QValidator.State.Invalid, string, pos)
        return (QValidator.State.Acceptable, string, pos)


class InheritsDialog(QDialog):
    def __init__(self, module):
        super().__init__()
        self.setWindowTitle("Choose your kinds of scenes")
        self.setLayout(QVBoxLayout())
        self.setModal(True)
        self.module = module or manim
        self.initUI()

    def initUI(self):
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
        if not self.scene_name.text():
            QMessageBox.critical(
                self, "Error", "You must choose a name for your scene")
            return None
        mro = []
        for checkbox, scene_type in zip(self.checkboxes, self.scene_types):
            if checkbox.isChecked():
                mro.append(scene_type)
        # We don't want to get an error if we choose two classes that inherit from each other
        mro = [scene_type for scene_type in mro for scene_type2 in mro if not issubclass(
            scene_type2, scene_type) and scene_type2 is not scene_type]
        if not any(issubclass(scene_type, LiveScene) for scene_type in mro):
            mro.insert(0, LiveScene)
        mro_without_live_scene = [scene_type for scene_type in mro if not issubclass(
            scene_type, LiveScene)] or [Scene]
        return type(self.scene_name.text(), tuple(mro), {"communicate": communicate})(communicate=communicate, mro_without_live_scene=mro_without_live_scene)
