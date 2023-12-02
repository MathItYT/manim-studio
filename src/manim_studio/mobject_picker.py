from manim import (
    Text,
    Mobject,
    Camera,
    MathTex,
    Tex,
    ImageMobject,
    Circle,
    Line,
    Square,
    Rectangle,
    SVGMobject
)
from manimpango import list_fonts
from manim_studio.communicate import Communicate
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QDialog,
    QLineEdit,
    QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize
from pathlib import Path
import importlib
import numpy as np
import time


def get_image_for_mobject() -> Path:
    manim_studio = importlib.import_module("manim_studio")
    manim_studio_path = Path(manim_studio.__file__).parent
    assets_path = manim_studio_path / "assets"
    return assets_path / "duck.jpg"


def get_svg_for_mobject() -> Path:
    manim_studio = importlib.import_module("manim_studio")
    manim_studio_path = Path(manim_studio.__file__).parent
    assets_path = manim_studio_path / "assets"
    return assets_path / "svg_file.svg"


class MobjectPicker(QScrollArea):
    def __init__(
        self,
        communicate: Communicate,
        editor,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.setWindowTitle("Manim Studio - Mobject Picker")
        self.communicate = communicate
        self.editor = editor
        self._setup_compatible_mobjects()
        self._setup_ui()

    def _setup_compatible_mobjects(self):
        self.compatible_mobjects: list[type[Mobject]] = [
            Text,
            MathTex,
            Tex,
            ImageMobject,
            Circle,
            Line,
            Square,
            Rectangle,
            SVGMobject
        ]
        self.sample_mobjects: list[Mobject] = [
            Text("Text"),
            MathTex("x^2 + y^2 = z^2"),
            Tex("\\LaTeX"),
            ImageMobject(get_image_for_mobject()),
            Circle(),
            Line(),
            Square(),
            Rectangle(),
            SVGMobject(get_svg_for_mobject())
        ]

    def _setup_ui(self):
        self._setup_images()
        self._setup_buttons_container()
        self._setup_scroll_area()
        self._setup_mobject_buttons()

    def _setup_images(self):
        buff = 0.1
        self.images = []
        for mobject in self.sample_mobjects:
            max_size = max(mobject.width, mobject.height)
            camera = Camera(frame_width=max_size + buff,
                            frame_height=max_size + buff, pixel_width=300, pixel_height=300)
            self.images.append(mobject.center().get_image(camera))

    def _setup_buttons_container(self):
        self.buttons_container = QWidget()
        self.buttons_container.setLayout(QGridLayout())
        self.buttons_container.layout().setContentsMargins(0, 0, 0, 0)
        self.buttons_container.layout().setSpacing(0)

    def _setup_scroll_area(self):
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidget(self.buttons_container)

    def _setup_mobject_buttons(self):
        self.mobject_buttons = []
        for type_, image in zip(self.compatible_mobjects, self.images):
            button = QPushButton()
            image = np.array(image)
            button.setIcon(QIcon(QPixmap.fromImage(
                QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888))))
            button.setIconSize(QSize(300, 300))
            button.setFixedSize(300, 300)
            button.clicked.connect(
                lambda _, type_=type_: self._on_mobject_button_clicked(type_))
            self.mobject_buttons.append(button)

        for index, button in enumerate(self.mobject_buttons):
            self.buttons_container.layout().addWidget(
                button, index // 2, index % 2)

    def _on_mobject_button_clicked(self, mobject_type: type[Mobject]):
        dialog = QDialog()
        dialog.setWindowTitle(f"Add {mobject_type.__name__}")
        dialog.setModal(True)
        dialog.setLayout(QVBoxLayout())
        mobject_name = QLineEdit()
        mobject_name.setPlaceholderText("Mobject Name")
        dialog.layout().addWidget(mobject_name)
        dialog.layout().addWidget(QPushButton("Add"))
        dialog.layout().itemAt(1).widget().clicked.connect(
            lambda: self._on_add_button_clicked(dialog, mobject_type, mobject_name))
        dialog.exec()

    def _on_add_button_clicked(self, dialog: QDialog, mobject_type: type[Mobject], mobject_name: QLineEdit):
        name = mobject_name.text()
        if name == "":
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText("Please enter a name")
            alert.exec()
            return
        if hasattr(self.editor.scene, name):
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText("Name already exists")
            alert.exec()
            return
        FUNCTION_MAP = {
            Text: self._add_text,
            MathTex: self._add_math_tex,
            Tex: self._add_tex,
            ImageMobject: self._add_image,
            Circle: self._add_circle,
            Line: self._add_line,
            Square: self._add_square,
            Rectangle: self._add_rectangle,
            SVGMobject: self._add_svg
        }
        FUNCTION_MAP[mobject_type](name)
        dialog.close()

    def _add_text(self, name: str):
        if name + "_edit" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_edit is a controller that already exists")
            alert.exec()
            return
        if name + "_font_dropdown" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_font_dropdown is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Text("{name}")
self.add(self.{name})""".strip())
        self.communicate.add_text_editor_to_editor.emit(name + "_edit", name)
        self.communicate.add_dropdown_to_editor.emit(
            name + "_font_dropdown", list_fonts(), "Times New Roman")
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
self.{name} = Text(self.{name}_edit.get_value(), font=self.{name}_font_dropdown.get_value())
self.add(self.{name})
        """.strip())

    def _add_math_tex(self, name: str):
        if name + "_edit" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_edit is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = MathTex("\\text{{{name}}}")
self.add(self.{name})""".strip())
        self.communicate.add_text_editor_to_editor.emit(
            name + "_edit", f"\\text{{{name}}}")
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
try:
    self.{name} = MathTex(self.{name}_edit.get_value())
except ValueError:
    self.print_gui("Invalid LaTeX")
    self.{name} = MathTex("\\text{{Invalid \\LaTeX}}").set_color(RED)
    self.add(self.{name})
else:
    self.add(self.{name})
        """.strip())

    def _add_tex(self, name: str):
        if name + "_edit" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_edit is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Tex("{name}")
self.add(self.{name})""".strip())
        self.communicate.add_text_editor_to_editor.emit(
            name + "_edit", name)
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
try:
    self.{name} = Tex(self.{name}_edit.get_value())
except ValueError:
    self.print_gui("Invalid LaTeX")
    self.{name} = Tex("Invalid LaTeX").set_color(RED)
    self.add(self.{name})
else:
    self.add(self.{name})
        """.strip())

    def _add_image(self, name: str):
        if name + "_file_widget" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_file_widget is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = ImageMobject(get_image_for_mobject())
self.add(self.{name})""".strip())
        self.communicate.add_file_widget_to_editor.emit(
            name + "_file_widget", "Image Files (*.png *.jpg *.jpeg)")
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
try:
    self.{name} = ImageMobject(self.{name}_file_widget_path.get_value())
except OSError:
    self.print_gui("Invalid Image")
    self.{name} = ImageMobject(get_image_for_mobject())
    self.add(self.{name})
else:
    self.add(self.{name})
        """.strip())
        while not hasattr(self.editor.scene, name + "_file_widget_size"):
            time.sleep(0)
        self.editor.controls[name + "_file_widget"].select_file_command(
            get_image_for_mobject())

    def _add_circle(self, name: str):
        if name + "_radius" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_radius is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Circle()
self.add(self.{name})""".strip())
        self.communicate.add_spin_box_to_editor.emit(
            name + "_radius", 1.0)
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
self.{name} = Circle(radius=self.{name}_radius.get_value())
self.add(self.{name})
        """.strip())
        self.editor.controls[name + "_radius"].setValue(1.0)

    def _add_line(self, name: str):
        if name + "_start" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_start is a controller that already exists")
            alert.exec()
            return
        if name + "_end" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_end is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Line()
self.add(self.{name})""".strip())
        self.communicate.add_position_control_to_editor.emit(
            name + "_start", np.array([0.0, 0.0, 0.0]))
        self.communicate.add_position_control_to_editor.emit(
            name + "_end", np.array([1.0, 0.0, 0.0]))
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
self.{name} = Line(self.{name}_start.get_center(), self.{name}_end.get_center())
self.add(self.{name})
        """.strip())
        self.editor.controls[name +
                             "_start"].x_.setValue(-1.0)
        self.editor.controls[name +
                             "_start"].y_.setValue(0.0)
        self.editor.controls[name +
                             "_start"].z_.setValue(0.0)
        self.editor.controls[name + "_end"].x_.setValue(1.0)
        self.editor.controls[name + "_end"].y_.setValue(0.0)
        self.editor.controls[name + "_end"].z_.setValue(0.0)

    def _add_square(self, name: str):
        if name + "_side_length" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_side_length is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Square()
self.add(self.{name})""".strip())
        self.communicate.add_spin_box_to_editor.emit(
            name + "_side_length", 1.0)
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
self.{name} = Square(side_length=self.{name}_side_length.get_value())
self.add(self.{name})
        """.strip())
        self.editor.controls[name + "_side_length"].setValue(2.0)

    def _add_rectangle(self, name: str):
        if name + "_width" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_width is a controller that already exists")
            alert.exec()
            return
        if name + "_height" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_height is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        self.communicate.update_scene.emit(f"""
self.{name} = Rectangle()
self.add(self.{name})""".strip())
        self.communicate.add_spin_box_to_editor.emit(
            name + "_width", 1.0)
        self.communicate.add_spin_box_to_editor.emit(
            name + "_height", 1.0)
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
self.{name} = Rectangle(width=self.{name}_width.get_value(), height=self.{name}_height.get_value())
self.add(self.{name})
        """.strip())
        self.editor.controls[name + "_width"].setValue(4.0)
        self.editor.controls[name + "_height"].setValue(2.0)

    def _add_svg(self, name: str):
        if name + "_file_widget" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_file_widget is a controller that already exists")
            alert.exec()
            return
        if name + "_update_button" in self.editor.controls.keys():
            alert = QMessageBox()
            alert.setWindowTitle("Error")
            alert.setText(
                f"Name {name}_update_button is a controller that already exists")
            alert.exec()
            return
        warning = QMessageBox()
        warning.setWindowTitle("Warning")
        warning.setText(
            "SVGs are partially supported in ManimCE and may not render properly (e.g. gradients, filters, etc.)")
        warning.exec()
        self.communicate.update_scene.emit(f"""
self.{name} = SVGMobject(get_svg_for_mobject())
self.add(self.{name})""".strip())
        self.communicate.add_file_widget_to_editor.emit(
            name + "_file_widget", "SVG Files (*.svg)")
        self.communicate.add_button_to_editor.emit(name + "_update_button", f"""
self.remove(self.{name})
try:
    self.{name} = SVGMobject(self.{name}_file_widget_path.get_value())
except OSError:
    self.print_gui("Invalid SVG")
    self.{name} = SVGMobject(get_svg_for_mobject())
    self.add(self.{name})
else:
    self.add(self.{name})
        """.strip())
        while not hasattr(self.editor.scene, name + "_file_widget_size"):
            time.sleep(0)
        self.editor.controls[name + "_file_widget"].select_file_command(
            get_svg_for_mobject())
