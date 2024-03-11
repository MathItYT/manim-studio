import string

from PyQt6.QtWidgets import QLabel, QComboBox, QInputDialog, QMessageBox
from PyQt6.QtGui import QMouseEvent

from manim import (
    Scene,
    Circle,
    RegularPolygon,
    Line,
    MathTex,
    Text,
    Mobject,
    DL,
    UR
)

import numpy as np

from .api import ManimStudioAPI
from .utils import qt_coords_to_manim_coords, make_snake_case


class Preview(QLabel):
    def __init__(
        self,
        window_size: tuple[int, int],
        mobject_picker_combobox: QComboBox,
        scene: Scene
    ):
        super().__init__()
        self.saved_state = None
        self.setting_radius = None
        self.setting_line_start = None
        self.setting_line_end = None
        self.mobject_to_put = None
        self.setting_mathtex_size = None
        self.mathtex_string = None
        self.setting_text_size = None
        self.text_string = None
        self.scene = scene
        self.mobject_picker_combobox = mobject_picker_combobox
        self.setMouseTracking(True)

        window_width, window_height = window_size
        max_width = window_width // 2
        max_height = window_height // 2
        pixel_width, pixel_height = scene.camera.pixel_width, scene.camera.pixel_height
        aspect_ratio = pixel_width / pixel_height

        if aspect_ratio > max_width / max_height:
            width = max_width
            height = max_width // aspect_ratio
        else:
            width = int(max_height * aspect_ratio)
            height = max_height

        self.setFixedSize(width, height)
    
    def add_mobject(self, mobject: Mobject):
        if isinstance(mobject, Circle):
            self.setting_radius = mobject
            return
        if isinstance(mobject, RegularPolygon):
            number_of_sides = QInputDialog.getInt(self, "Set number of sides", "Enter the number of sides (default: 6)")[0]
            number_of_sides = number_of_sides or 6
            side_length = QInputDialog.getDouble(self, "Set side length", "Enter the side length (default: 1)")[0]
            side_length = side_length or 1
            # Using radius formula given the side length and number of sides
            radius = side_length / (2 * np.sin(np.pi / number_of_sides))
            mobject = RegularPolygon(number_of_sides, radius=radius).move_to(mobject.get_center())
            name = QInputDialog.getText(self, "Set name", "Enter the mobject's name (default: reg_poly)")[0]
            name = make_snake_case(name) or "reg_poly"
            self.scene.__dict__ = self.saved_state
            self.saved_state = None
            ManimStudioAPI.execute(f"""
{name} = RegularPolygon({number_of_sides}, radius={radius}).move_to(RIGHT*{mobject.get_x()} + UP*{mobject.get_y()})
self.add({name})
""".strip())
            self.mobject_picker_combobox.setDisabled(False)
            return
        if isinstance(mobject, Line):
            self.setting_line_start = mobject
            return
        if isinstance(mobject, MathTex):
            center = mobject.get_center()
            error = True
            while error:
                try:
                    text = QInputDialog.getText(self, "Set text", "Enter the text (default: x^2)")[0]
                    text = text or "x^2"
                    mobject.become(MathTex(text).move_to(center))
                except (ValueError, RuntimeError):
                    QMessageBox.critical(self, "Error", "Invalid LaTeX code, try again")
                else:
                    error = False
            QMessageBox.information(self, "Info", "LaTeX rendered successfully")
            self.setting_mathtex_size = mobject
            self.mathtex_string = text
            return
        if isinstance(mobject, Text):
            center = mobject.get_center()
            text = QInputDialog.getText(self, "Set text", "Enter the text (default: T)")[0]
            text = text or "T"
            mobject.become(Text(text).move_to(center))
            self.setting_text_size = mobject
            self.text_string = text
            return
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        super().mouseMoveEvent(a0)
        if (
            not self.mobject_to_put
            and not self.setting_radius
            and not self.setting_line_start
            and not self.setting_line_end
            and not self.setting_mathtex_size
            and not self.setting_text_size
        ):
            return
        qt_coords = a0.globalPosition()
        frame_x, frame_y = qt_coords_to_manim_coords(
            self.scene,
            qt_coords.x(),
            qt_coords.y(),
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )
        frame_pos = np.array([frame_x, frame_y, 0])
        if self.setting_radius:
            center = self.setting_radius.get_center()
            radius = np.linalg.norm(frame_pos - center)
            self.setting_radius.become(Circle(radius=radius).move_to(center))
            self.setting_radius.radius = radius
            return
        if self.setting_line_start:
            self.setting_line_start.put_start_and_end_on(frame_pos, self.setting_line_start.get_end())
            return
        if self.setting_line_end:
            self.setting_line_end.put_start_and_end_on(self.setting_line_end.get_start(), frame_pos)
            return
        if self.setting_mathtex_size:
            center = self.setting_mathtex_size.get_center()
            self.setting_mathtex_size.scale_to_fit_height(2 * abs(frame_y - self.setting_mathtex_size.get_y()))
            self.setting_mathtex_size.move_to(center)
            return
        if self.setting_text_size:
            center = self.setting_text_size.get_center()
            self.setting_text_size.scale_to_fit_height(2 * abs(frame_y - self.setting_text_size.get_y()))
            self.setting_text_size.move_to(center)
            return
        if isinstance(self.mobject_to_put, type):
            self.saved_state = self.scene.__dict__.copy()
            if self.mobject_to_put == Circle:
                self.mobject_to_put = Circle()
            elif self.mobject_to_put == RegularPolygon:
                self.mobject_to_put = RegularPolygon(6)
            elif self.mobject_to_put == Line:
                self.mobject_to_put = Line(DL, UR)
            elif self.mobject_to_put == MathTex:
                self.mobject_to_put = MathTex("x^2")
            elif self.mobject_to_put == Text:
                self.mobject_to_put = Text("T")
            self.scene.add(self.mobject_to_put)
        self.mobject_to_put.move_to(frame_pos)
    
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        super().mousePressEvent(a0)
        if (
            not self.mobject_to_put
            and not self.setting_radius
            and not self.setting_line_start
            and not self.setting_line_end
            and not self.setting_mathtex_size
            and not self.setting_text_size
        ):
            return
        if self.setting_radius:
            circle = self.setting_radius
            self.setting_radius = None
            name = QInputDialog.getText(self, "Set name", "Enter the circle's name (default: circ)")[0]
            name = make_snake_case(name) or "circ"
            self.scene.__dict__ = self.saved_state
            self.saved_state = None
            ManimStudioAPI.execute(f"""
{name} = Circle(radius={circle.radius}).move_to(RIGHT*{circle.get_x()} + UP*{circle.get_y()})
self.add({name})
""".strip())
            self.mobject_picker_combobox.setDisabled(False)
            return
        if self.setting_line_start:
            self.setting_line_end = self.setting_line_start
            self.setting_line_start = None
            return
        if self.setting_line_end:
            line = self.setting_line_end
            self.setting_line_end = None
            name = QInputDialog.getText(self, "Set name", "Enter the line's name (default: line)")[0]
            name = make_snake_case(name) or "line"
            self.scene.__dict__ = self.saved_state
            self.saved_state = None
            start_x, start_y, _ = line.get_start()
            end_x, end_y, _ = line.get_end()
            ManimStudioAPI.execute(f"""
{name} = Line(RIGHT*{start_x} + UP*{start_y}, RIGHT*{end_x} + UP*{end_y})
self.add({name})
""".strip())
            self.mobject_picker_combobox.setDisabled(False)
            return
        if self.setting_mathtex_size:
            mathtex = self.setting_mathtex_size
            self.setting_mathtex_size = None
            text = QInputDialog.getText(self, "Set name", "Enter the MathTex's name (default: math_tex)")[0]
            text = make_snake_case(text) or "math_tex"
            self.scene.__dict__ = self.saved_state
            self.saved_state = None
            ManimStudioAPI.execute(f"""
{text} = MathTex({repr(self.mathtex_string)}).scale_to_fit_height({mathtex.height}).move_to(RIGHT*{mathtex.get_x()} + UP*{mathtex.get_y()})
self.add({text})
""".strip())
            self.mathtex_string = None
            self.mobject_picker_combobox.setDisabled(False)
            return
        if self.setting_text_size:
            text = self.setting_text_size
            self.setting_text_size = None
            name = QInputDialog.getText(self, "Set name", "Enter the Text's name (default: text)")[0]
            name = make_snake_case(name) or "text"
            self.scene.__dict__ = self.saved_state
            self.saved_state = None
            ManimStudioAPI.execute(f"""
{name} = Text({repr(self.text_string)}).scale_to_fit_height({text.height}).move_to(RIGHT*{text.get_x()} + UP*{text.get_y()})
self.add({name})
""".strip())
            self.text_string = None
            self.mobject_picker_combobox.setDisabled(False)
            return
        mobject = self.mobject_to_put
        self.mobject_to_put = None
        self.add_mobject(mobject)
