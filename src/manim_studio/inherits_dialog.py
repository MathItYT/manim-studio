from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QCheckBox
import manim
from .live_scene import LiveScene


class InheritsDialog(QDialog):
    def __init__(self, scene_type=LiveScene, namespace=None):
        super().__init__()
        self.layout_ = QVBoxLayout()
        self.setLayout(self.layout_)
        self.setWindowTitle("Manim Studio - Use base class")
        self.setGeometry(0, 0, 400, 300)
        self.group_box = QGroupBox("Choose base classes")
        self.group_box.setLayout(QVBoxLayout())
        # Allow multiple inheritance
        self.namespace = namespace.__dict__ if namespace is not None else {}
        self.namespace.update(manim.__dict__)
        for name, obj in self.namespace.items():
            if isinstance(obj, type) and issubclass(obj, manim.Scene) and obj not in [manim.Scene, LiveScene]:
                checkbox = QCheckBox(name)
                checkbox.setChecked(False)
                self.group_box.layout().addWidget(checkbox)
        self.layout_.addWidget(self.group_box)
        self.scene_type = scene_type

    def set_scene_type_base_classes(self):
        for i in range(self.group_box.layout().count()):
            checkbox = self.group_box.layout().itemAt(i).widget()
            if checkbox.isChecked():
                if manim.Scene in self.scene_type.__bases__:
                    self.scene_type.__bases__ = tuple(
                        item for item in self.scene_type.__bases__ if item != manim.Scene)
                self.scene_type.__bases__ = self.scene_type.__bases__ + \
                    (self.namespace[checkbox.text()],)
        return self.scene_type
