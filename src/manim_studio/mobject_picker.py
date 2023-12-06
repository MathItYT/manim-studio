from PyQt6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QDialog,
    QLineEdit,
    QComboBox,
    QGroupBox
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
from manim import (
    Text,
    MathTex,
    Tex,
    Circle,
    ImageMobject,
    Square,
    Rectangle,
    SVGMobject,
    VGroup,
    BLUE,
    RIGHT,
    Mobject,
    Camera,
    VMobject
)
import importlib
from pathlib import Path
import numpy as np
from manimpango import list_fonts
import sys


class RefreshDropdownVGroupButton(QPushButton):
    pass


class EditVMobjectsDropdown(QGroupBox):
    def __init__(self, name: str, editor):
        super().__init__()
        self.name = name
        self.editor = editor
        self.init_ui()

    def init_ui(self):
        self.setTitle("Edit VMobjects")
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.dropdown = QComboBox()
        self.dropdown.addItems([vmob for vmob in vars(self.editor.scene).keys(
        ) if isinstance(vars(self.editor.scene)[vmob], VMobject) and vmob != self.name])
        self.layout().addWidget(self.dropdown)
        self.add_vmobject_button = QPushButton("Add VMobject")
        self.add_vmobject_button.clicked.connect(self.add_vmobject)
        self.layout().addWidget(self.add_vmobject_button)
        self.remove_vmobject_button = QPushButton("Remove VMobject")
        self.remove_vmobject_button.clicked.connect(self.remove_vmobject)
        self.layout().addWidget(self.remove_vmobject_button)
        self.clear_vmobjects_button = QPushButton("Clear VMobjects")
        self.clear_vmobjects_button.clicked.connect(self.clear_vmobjects)
        self.layout().addWidget(self.clear_vmobjects_button)
        self.current_vmobjects_label = QLabel("Current VMobjects in VGroup: ")
        self.layout().addWidget(self.current_vmobjects_label)
        self.refresh_vmobjects_button = QPushButton("Refresh VMobjects")
        self.refresh_vmobjects_button.clicked.connect(
            lambda: self.update_current_vmobjects_label(
                getattr(self.editor.scene, self.name).submobjects))
        self.layout().addWidget(self.refresh_vmobjects_button)

    def add_vmobject(self):
        self.editor.communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).add(getattr(self, {self.dropdown.currentText().__repr__()}))")
        self.update_current_vmobjects_label(getattr(
            self.editor.scene, self.name).submobjects + [getattr(self.editor.scene, self.dropdown.currentText())])

    def update_current_vmobjects_label(self, submobjects: list[VMobject]):
        names = [self.get_name(vmob) for vmob in submobjects]
        self.current_vmobjects_label.setText(
            "Current VMobjects in VGroup: " + ", ".join(names))
        self.dropdown.clear()
        self.dropdown.addItems([vmob for vmob in vars(self.editor.scene).keys(
        ) if isinstance(vars(self.editor.scene)[vmob], VMobject) and vmob != self.name])

    def get_name(self, vmob: VMobject):
        for name, value in vars(self.editor.scene).items():
            if value is vmob:
                return name
        return f"Unknown {type(vmob).__name__}"

    def remove_vmobject(self):
        self.editor.communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).remove(getattr(self, {self.dropdown.currentText().__repr__()}))")
        self.update_current_vmobjects_label([vmob for vmob in getattr(
            self.editor.scene, self.name).submobjects if vmob is not getattr(self.editor.scene, self.dropdown.currentText())])

    def clear_vmobjects(self):
        self.editor.communicate.update_scene.emit(
            f"getattr(self, {self.name.__repr__()}).submobjects.clear()")
        self.update_current_vmobjects_label([])


def get_duck_image():
    manim_studio = importlib.import_module("manim_studio")
    manim_studio_path = Path(manim_studio.__file__).parent
    return str(manim_studio_path / "assets" / "duck.jpg")


def get_svg_file():
    manim_studio = importlib.import_module("manim_studio")
    manim_studio_path = Path(manim_studio.__file__).parent
    return str(manim_studio_path / "assets" / "svg_file.svg")


class MobjectPicker(QScrollArea):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setGeometry(0, 0, 600, 600)
        self.setWindowTitle("Mobject Picker")
        self.init_ui()

    def init_ui(self):
        self.supported_mobjects = [
            Text,
            MathTex,
            Tex,
            Circle,
            ImageMobject,
            Square,
            Rectangle,
            SVGMobject,
            VGroup
        ]
        self.sample_mobjects = [
            Text("Text"),
            MathTex("\\int_0^\\infty x^2 dx"),
            Tex("\\LaTeX"),
            Circle(),
            ImageMobject(get_duck_image()),
            Square(color=BLUE),
            Rectangle(),
            SVGMobject(get_svg_file()),
            VGroup(Circle(), Square(color=BLUE)).arrange(RIGHT)
        ]
        self.setWidgetResizable(True)
        self.setWidget(QWidget())
        self.widget().setLayout(QGridLayout(self.widget()))
        self.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.widget().layout().setSpacing(0)
        for i, mobject in enumerate(self.sample_mobjects):
            widget = QWidget()
            widget.setLayout(QVBoxLayout(widget))
            widget.layout().setContentsMargins(0, 0, 0, 0)
            widget.layout().setSpacing(0)
            widget.layout().addWidget(self.get_image_button(mobject))
            widget.layout().addWidget(QLabel(type(mobject).__name__))
            self.widget().layout().addWidget(widget, i // 3, i % 3)

    def get_image_for_sample_mobject(self, mobject: Mobject):
        camera = Camera(
            frame_center=mobject.get_center(),
            frame_width=max(mobject.width, mobject.height) + 0.1,
            frame_height=max(mobject.width, mobject.height) + 0.1,
            pixel_height=200,
            pixel_width=200
        )
        img = mobject.get_image(camera)
        return np.array(img)

    def get_image_button(self, mobject: Mobject):
        image = self.get_image_for_sample_mobject(mobject)
        button = QPushButton()
        button.setIcon(QIcon(QPixmap.fromImage(QImage(
            image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888))))
        button.setIconSize(QSize(image.shape[1], image.shape[0]))
        button.setFixedSize(image.shape[1], image.shape[0])
        FUNCTION_MAP = {
            Text: self._add_text,
            MathTex: self._add_math_tex,
            Tex: self._add_tex,
            Circle: self._add_circle,
            ImageMobject: self._add_image_mobject,
            Square: self._add_square,
            Rectangle: self._add_rectangle,
            SVGMobject: self._add_svg_mobject,
            VGroup: self._add_vgroup
        }
        button.clicked.connect(FUNCTION_MAP[type(mobject)])
        return button

    def exec_name_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("Add Text")
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.label = QLabel(
            "Enter the mobject's name (it will be saved as an attribute of the scene):")
        dialog.layout().addWidget(dialog.label)
        dialog.line_edit = QLineEdit()
        dialog.layout().addWidget(dialog.line_edit)
        dialog.button = QPushButton("Add")
        dialog.button.clicked.connect(dialog.accept)
        dialog.layout().addWidget(dialog.button)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Accepted:
            return dialog.line_edit.text() or None
        return None

    def _add_text(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_edit already exists")
            return
        if f"{name}_font_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_font_edit already exists")
            return
        if f"{name}_font_size_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_font_size_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, Text({name.__repr__()}, font={'Times New Roman'.__repr__()}, font_size=48))")
        self.editor.communicate.print_gui.emit(
            f"Added Text with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        text_box = self.editor.add_text_box_command(f"{name}_edit")
        text_box.text_edit.setText(name)
        font_edit = self.editor.add_dropdown_command(
            f"{name}_font_edit", list_fonts())
        font_edit.dropdown.setCurrentText("Times New Roman")
        self.editor.add_spin_box_command(
            f"{name}_font_size_edit", "8", "192", "48")
        self.editor.add_button_command(f"{name}_update", f"""
getattr(self, {name.__repr__()}).become(
    Text(getattr(self, {f"{name}_edit".__repr__()}).get_value(), font=getattr(self, {f"{name}_font_edit".__repr__()}).get_value(), font_size=getattr(self, {f"{name}_font_size_edit".__repr__()}).get_value()))
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_math_tex(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, MathTex({f"\\text{{{name}}}".__repr__()}))")
        self.editor.communicate.print_gui.emit(
            f"Added MathTex with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        text_box = self.editor.add_text_box_command(f"{name}_edit")
        text_box.text_edit.setText(f"\\text{{{name}}}")
        self.editor.add_button_command(f"{name}_update", f"""
try:
    getattr(self, {name.__repr__()}).become(
        MathTex(getattr(self, {f"{name}_edit".__repr__()}).get_value()))
except ValueError:
    pass
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_tex(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, Tex({f"\\text{{{name}}}".__repr__()}))")
        self.editor.communicate.print_gui.emit(
            f"Added Tex with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        text_box = self.editor.add_text_box_command(f"{name}_edit")
        text_box.text_edit.setText(f"\\text{{{name}}}")
        self.editor.add_button_command(f"{name}_update", f"""
try:
    getattr(self, {name.__repr__()}).become(
        Tex(getattr(self, {f"{name}_edit".__repr__()}).get_value()))
except ValueError:
    pass
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_circle(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_radius_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_radius_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, Circle())")
        self.editor.communicate.print_gui.emit(
            f"Added Circle with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        self.editor.add_spin_box_command(
            f"{name}_radius_edit", "0", f"{sys.float_info.max}", "1")
        self.editor.add_button_command(f"{name}_update", f"""
getattr(self, {name.__repr__()}).become(
    Circle(radius=getattr(self, {f"{name}_radius_edit".__repr__()}).get_value()))
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_image_mobject(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_path_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_path_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, ImageMobject({get_duck_image().__repr__()}))")
        self.editor.communicate.print_gui.emit(
            f"Added ImageMobject with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        file_selector = self.editor.add_file_selector_command(
            f"{name}_path_edit")
        file_selector.select_file_command(get_duck_image())
        self.editor.add_button_command(f"{name}_update", f"""
if getattr(self, {f"{name}_path_edit".__repr__()}).get_value() != "":
    self.remove(getattr(self, {name.__repr__()}))
    setattr(self, {name.__repr__()}, ImageMobject(
        getattr(self, {f"{name}_path_edit".__repr__()}).get_value()))
    self.print_gui(
        "ImageMobject updated. To see on screen, press 'Add to Scene' button.")
else:
    self.print_gui("No file selected. The ImageMobject was not updated.")
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_square(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_side_length_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_side_length_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, Square())")
        self.editor.communicate.print_gui.emit(
            f"Added Square with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        self.editor.add_spin_box_command(
            f"{name}_side_length_edit", "0", f"{sys.float_info.max}", "2")
        self.editor.add_button_command(f"{name}_update", f"""
getattr(self, {name.__repr__()}).become(
    Square(side_length=getattr(self, {f"{name}_side_length_edit".__repr__()}).get_value()))
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_rectangle(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_width_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_width_edit already exists")
            return
        if f"{name}_height_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_height_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, Rectangle())")
        self.editor.communicate.print_gui.emit(
            f"Added Rectangle with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        self.editor.add_spin_box_command(
            f"{name}_width_edit", "0", f"{sys.float_info.max}", "4")
        self.editor.add_spin_box_command(
            f"{name}_height_edit", "0", f"{sys.float_info.max}", "2")
        self.editor.add_button_command(f"{name}_update", f"""
getattr(self, {name.__repr__()}).become(
    Rectangle(width=getattr(self, {f"{name}_width_edit".__repr__()}).get_value(), height=getattr(self, {f"{name}_height_edit".__repr__()}).get_value()))
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_svg_mobject(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_path_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_path_edit already exists")
            return
        if f"{name}_update" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_update already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, SVGMobject({get_svg_file().__repr__()}))")
        self.editor.communicate.print_gui.emit(
            f"Added SVGMobject with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        file_selector = self.editor.add_file_selector_command(
            f"{name}_path_edit")
        file_selector.select_file_command(get_svg_file())
        self.editor.add_button_command(f"{name}_update", f"""
if getattr(self, {f"{name}_path_edit".__repr__()}).get_value() != "":
    self.remove(getattr(self, {name.__repr__()}))
    setattr(self, {name.__repr__()}, SVGMobject(
        getattr(self, {f"{name}_path_edit".__repr__()}).get_value()))
    self.print_gui(
        "SVGMobject updated. To see on screen, press 'Add to Scene' button.")
else:
    self.print_gui("No file selected. The SVGMobject was not updated.")
""".strip())
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())

    def _add_vgroup(self):
        name = self.exec_name_dialog()
        if name is None:
            self.editor.communicate.print_gui.emit("No name entered")
            return
        if f"{name}_vmobjects_edit" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_vmobjects_edit already exists")
            return
        if f"{name}_add_to_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_add_to_scene already exists")
            return
        if f"{name}_remove_from_scene" in self.editor.controls:
            self.editor.communicate.print_gui.emit(
                f"Control with name {name}_remove_from_scene already exists")
            return
        self.editor.communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, VGroup())")
        self.editor.communicate.print_gui.emit(
            f"Added VGroup with name {name}.\nTo see on screen, press 'Add to Scene' button.\nTo remove, press 'Remove from Scene' button.")
        self.editor.add_custom_control_command(
            f"{name}_vmobjects_edit", EditVMobjectsDropdown(name, self.editor))
        self.editor.add_button_command(f"{name}_add_to_scene", f"""
self.add(getattr(self, {name.__repr__()}))
""".strip())
        self.editor.add_button_command(f"{name}_remove_from_scene", f"""
self.remove(getattr(self, {name.__repr__()}))
""".strip())
