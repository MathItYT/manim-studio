from copy import copy
from pathlib import Path
from subprocess import Popen
import shutil

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QColorDialog,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QComboBox,
    QMenu,
    QScrollArea,
    QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QAction, QColor

from manim import (
    Scene,
    Camera,
    Circle,
    RegularPolygon,
    Line,
    MathTex,
    Text,
    VMobject,
    BLACK,
    DL,
    UR
)

from PIL.ImageQt import ImageQt
from PIL import Image

from .api import ManimStudioAPI
from .input_widgets.range_slider import RangeSlider
from .input_widgets.color_picker import ColorPicker
from .mobject_picker import MobjectPicker
from .preview import Preview
from .syntax_highlighting import PythonHighlighter
from .utils import make_camel_case


FILE_CONTENT_TEMPLATE = """
from manim import *
from manim_studio import *
%s

class %s(%s):
    def construct(self):
        super().construct()
%s
        hold_on(self, locals())

    def setup_deepness(self):
        super().setup_deepness()
        self.deepness += 1
""".strip()


CONTENT_IF_IMPORTED = """
from manim_studio.utils import import_from_file

from pathlib import Path


module = import_from_file(Path(%s))
""".lstrip()


class Window(QMainWindow):
    """A window to preview the scene."""

    def __init__(
        self,
        window_size: tuple[int, int],
        scene: Scene
    ):
        super().__init__(None)
        ManimStudioAPI.print_signal_wrapper.print_signal.connect(self.print_gui)
        ManimStudioAPI.print_signal_wrapper.show_error_signal.connect(self.show_error)
        self.setWindowTitle("Manim Studio")
        self.saved_file = None
        self.saved_scene_class_name = None
        self.scene = scene
        self.setMouseTracking(True)

        self.setCentralWidget(QWidget())
        layout = QHBoxLayout()
        self.centralWidget().setLayout(layout)
        v_layout_1 = QVBoxLayout()
        layout.addLayout(v_layout_1)
        v_layout_2 = QVBoxLayout()
        layout.addLayout(v_layout_2)

        edit_menu = QMenu("Edit", self)
        set_fill_color_action = QAction("Set Fill Color", self)
        set_fill_color_action.triggered.connect(self.set_fill_color)
        edit_menu.addAction(set_fill_color_action)
        set_stroke_color_action = QAction("Set Stroke Color", self)
        set_stroke_color_action.triggered.connect(self.set_stroke_color)
        edit_menu.addAction(set_stroke_color_action)
        set_stroke_width_action = QAction("Set Stroke Width", self)
        set_stroke_width_action.triggered.connect(self.set_stroke_width)
        edit_menu.addAction(set_stroke_width_action)
        self.menuBar().addMenu(edit_menu)

        input_widgets_menu = QMenu("Input Widgets", self)
        add_range_slider_action = QAction("Add Range Slider", self)
        add_range_slider_action.triggered.connect(self.add_range_slider)
        input_widgets_menu.addAction(add_range_slider_action)
        add_color_picker_action = QAction("Add Color Picker", self)
        add_color_picker_action.triggered.connect(self.add_color_picker)
        input_widgets_menu.addAction(add_color_picker_action)
        self.menuBar().addMenu(input_widgets_menu)

        self.menuBar().setNativeMenuBar(False)

        self.generate_python_file_button = QPushButton("Generate Python File")
        self.generate_python_file_button.clicked.connect(self.generate_python_file)
        v_layout_2.addWidget(self.generate_python_file_button)
        self.generate_video_file_button = QPushButton("Render Video File")
        self.generate_video_file_button.clicked.connect(self.render_video_file)
        v_layout_2.addWidget(self.generate_video_file_button)

        self.mobject_picker_combobox = QComboBox()
        self.setup_mobject_picker_combobox()
        v_layout_2.addWidget(self.mobject_picker_combobox)

        self.add_mobject_button = QPushButton("Add Mobject")
        self.add_mobject_button.setShortcut("Ctrl+A")
        self.add_mobject_button.clicked.connect(self.select_mobject)
        v_layout_2.addWidget(self.add_mobject_button)

        label = QLabel("Input Widgets")
        label.setFixedHeight(10)
        v_layout_2.addWidget(label)
        self.input_widgets_zone = QScrollArea()
        self.input_widgets_zone.setWidgetResizable(True)
        self.input_widgets_zone.setFixedHeight(window_size[1] // 2 - 100)
        self.input_widgets_zone.setFixedWidth(window_size[0] // 2 - 100)
        self.input_widgets_zone.setWidget(QWidget())
        self.input_widgets_zone.widget().setLayout(QVBoxLayout())
        v_layout_2.addWidget(self.input_widgets_zone)

        self.label = Preview(window_size, self.mobject_picker_combobox, scene)
        v_layout_1.addWidget(self.label)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write your code here")
        self.highlighter = PythonHighlighter(self.editor.document())
        self.editor.setFixedHeight(window_size[1] // 2 - 100)
        self.editor.setFixedWidth(window_size[0] // 2)
        self.editor.setContentsMargins(0, 0, 0, 0)
        self.editor.setStyleSheet("background-color: rgb(46, 46, 46);")
        v_layout_1.addWidget(self.editor)

        old_update_to_time = copy(scene.update_to_time)

        def update_to_time(time: float):
            old_update_to_time(time)
            self.update_image()
        
        scene.update_to_time = update_to_time

        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(lambda: self.execute(self.editor.toPlainText()))
        self.execute_button.setShortcut("Ctrl+Return")
        v_layout_1.addWidget(self.execute_button)
    
        plugins_menu = QMenu("Plugins", self)
        for name, module in ManimStudioAPI.plugins.items():
            plugin_menu = QAction(name, self)
            plugin_menu.triggered.connect(lambda: ManimStudioAPI.run_plugin(name))
            if hasattr(module, "init_widgets"):
                module.init_widgets(self)
            plugins_menu.addAction(plugin_menu)
        self.menuBar().addMenu(plugins_menu)

    def execute(self, code: str):
        setattr(self.scene, "code", code)
    
    def print_gui(self, text: str):
        QMessageBox.information(self, "Manim Studio - PrintGUI", text)
    
    def add_range_slider(self):
        variable_name, ok = QInputDialog.getText(self, "Variable Name", "Enter the name of the variable")
        if not ok:
            return
        minimum, ok = QInputDialog.getDouble(self, "Minimum Value", "Enter the minimum value", 0.0, -1000000.0, 1000000.0, 6)
        if not ok:
            return
        maximum, ok = QInputDialog.getDouble(self, "Maximum Value", "Enter the maximum value", 100.0, -1000000.0, 1000000.0, 6)
        if not ok:
            return
        step, ok = QInputDialog.getDouble(self, "Step", "Enter the step", 1.0, -1000000.0, 1000000.0, 6)
        if not ok:
            return
        value, ok = QInputDialog.getDouble(self, "Value", "Enter the value", 0.0, -1000000.0, 1000000.0, 6)
        if not ok:
            return
        range_slider = RangeSlider(variable_name, value, minimum, maximum, step, self.width())
        self.input_widgets_zone.widget().layout().addWidget(range_slider)
    
    def add_color_picker(self):
        variable_name, ok = QInputDialog.getText(self, "Variable Name", "Enter the name of the variable")
        if not ok:
            return
        color_picker = ColorPicker(variable_name, self.width())
        self.input_widgets_zone.widget().layout().addWidget(color_picker)
    
    def set_fill_color(self):
        mobject_picker = MobjectPicker(
            self.width(),
            self.scene.camera,
            VMobject
        )
        selected_mobject = mobject_picker.wait_for_selection()
        if selected_mobject is None:
            return
        name, selected_mobject = selected_mobject
        selected_mobject: VMobject
        color = selected_mobject.get_fill_color()
        (r, g, b), a = color.to_rgb(), selected_mobject.get_fill_opacity()
        color = int(r*255), int(g*255), int(b*255), int(a*255)
        fill_color = QColorDialog.getColor(QColor(*color), self, "Select Fill Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if not fill_color.isValid():
            return
        r, g, b, a = fill_color.getRgbF()
        ManimStudioAPI.scene.code = f"self.{name}.set_fill(rgb_to_color(({r}, {g}, {b})), {a})"
        QMessageBox.information(self, "Fill Color Set", "The fill color has been set successfully")
    
    def set_stroke_color(self):
        mobject_picker = MobjectPicker(
            self.width(),
            self.scene.camera,
            VMobject
        )
        selected_mobject = mobject_picker.wait_for_selection()
        if selected_mobject is None:
            return
        name, selected_mobject = selected_mobject
        selected_mobject: VMobject
        color = selected_mobject.get_stroke_color()
        (r, g, b), a = color.to_rgb(), selected_mobject.get_stroke_opacity()
        color = int(r*255), int(g*255), int(b*255), int(a*255)
        stroke_color = QColorDialog.getColor(QColor(*color), self, "Select Stroke Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if not stroke_color.isValid():
            return
        r, g, b, a = stroke_color.getRgbF()
        ManimStudioAPI.scene.code = f"self.{name}.set_stroke(rgb_to_color(({r}, {g}, {b})), opacity={a})"
        QMessageBox.information(self, "Stroke Color Set", "The stroke color has been set successfully")
    
    def set_stroke_width(self):
        mobject_picker = MobjectPicker(
            self.width(),
            self.scene.camera,
            VMobject
        )
        selected_mobject = mobject_picker.wait_for_selection()
        if selected_mobject is None:
            return
        name, selected_mobject = selected_mobject
        selected_mobject: VMobject
        stroke_width, ok = QInputDialog.getDouble(self, "Set Stroke Width", "Enter the stroke width", selected_mobject.get_stroke_width(), 0, 100, 1)
        if not ok:
            return
        ManimStudioAPI.scene.code = f"self.{name}.set_stroke(width={stroke_width})"
        QMessageBox.information(self, "Stroke Width Set", "The stroke width has been set successfully")
    
    def select_mobject(self):
        self.label.mobject_to_put = ManimStudioAPI.supported_mobjects[self.mobject_picker_combobox.currentText()]
        self.mobject_picker_combobox.setDisabled(True)
    
    def setup_mobject_picker_combobox(self):
        for mobject in ManimStudioAPI.supported_mobjects:
            if mobject == "Circle":
                camera = Camera(
                    pixel_width=1000,
                    pixel_height=1000,
                    frame_width=2.25,
                    frame_height=2.25,
                    background_opacity=0
                )
                self.mobject_picker_combobox.addItem(
                    QIcon(QPixmap.fromImage(ImageQt(Circle(stroke_width=16) \
                                                    .get_image(camera)))),
                    "Circle"
                )
            elif mobject == "Regular Polygon":
                camera = Camera(
                    pixel_width=1000,
                    pixel_height=1000,
                    frame_width=2.25,
                    frame_height=2.25,
                    background_opacity=0
                )
                self.mobject_picker_combobox.addItem(
                    QIcon(QPixmap.fromImage(ImageQt(RegularPolygon(6, stroke_width=16) \
                                                    .get_image(camera)))),
                    "Regular Polygon"
                )
            elif mobject == "Line":
                camera = Camera(
                    pixel_width=1000,
                    pixel_height=1000,
                    frame_width=2.25,
                    frame_height=2.25,
                    background_opacity=0
                )
                self.mobject_picker_combobox.addItem(
                    QIcon(QPixmap.fromImage(ImageQt(Line(
                        DL, UR, stroke_width=16, color=BLACK
                    ).get_image(camera)))),
                    "Line"
                )
            elif mobject == "MathTex":
                camera = Camera(
                    pixel_width=1000,
                    pixel_height=1000,
                    frame_width=2.25,
                    frame_height=2.25,
                    background_opacity=0
                )
                self.mobject_picker_combobox.addItem(
                    QIcon(QPixmap.fromImage(ImageQt(MathTex("x^2", color=BLACK) \
                                                    .scale_to_fit_width(2) \
                                                    .get_image(camera)))),
                    "MathTex"
                )
            elif mobject == "Text":
                camera = Camera(
                    pixel_width=1000,
                    pixel_height=1000,
                    frame_width=2.25,
                    frame_height=2.25,
                    background_opacity=0
                )
                self.mobject_picker_combobox.addItem(
                    QIcon(QPixmap.fromImage(ImageQt(Text("T", color=BLACK) \
                                                    .scale_to_fit_width(2) \
                                                    .get_image(camera)))),
                    "Text"
                )

    def show_error(self, error: Exception):
        """Show the given error in the GUI."""
        QMessageBox.critical(
            self,
            "Error",
            "¡Ha ocurrido un error!\n\n"
            f"{error.__class__.__name__}: {error}"
        )

    def generate_python_file(self):
        self.scene.code = ""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Python File", "", "Python Files (*.py)")
        if not file_name:
            return
        scene_class_name = QInputDialog.getText(self, "Scene Class Name", "Enter the name of the scene class")[0]
        scene_class_name = make_camel_case(
            scene_class_name,
            f"{ManimStudioAPI.scene.__class__.__name__}Generated"
        )
        codes = ManimStudioAPI.codes
        codes = [line for code in codes for line in code.split("\n")]
        with open(file_name, "w") as f:
            f.write(FILE_CONTENT_TEMPLATE % (
                CONTENT_IF_IMPORTED % repr(str(Path(ManimStudioAPI.path_to_file).absolute()))
                if ManimStudioAPI.path_to_file else "",
                scene_class_name,
                f"module.{ManimStudioAPI.scene.__class__.__name__}"
                if ManimStudioAPI.scene.__class__ != Scene else "Scene",
                "\n".join(8*" " + line for line in codes)
            ))
        self.saved_file = file_name
        self.saved_scene_class_name = scene_class_name
        QMessageBox.information(self, "File Saved", "The file has been saved successfully")
    
    def render_video_file(self):
        if not self.saved_file:
            QMessageBox.critical(self, "Error", "You must generate a Python file before rendering")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video File", "", "Video Files (*.mp4)")
        if not file_name:
            return
        preview = QMessageBox.question(self, "Preview", "Do you want to preview the video?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        path = Path(file_name)

        process = Popen(
            [
                "manim",
                self.saved_file,
                self.saved_scene_class_name,
                "-o",
                f"{path.stem}.mp4",
                "--format=mp4",
            ] + (["-p"] if preview == QMessageBox.StandardButton.Yes else [])
        )
        process.wait()

        output_path = Path("media") / "videos" / Path(self.saved_file).stem / "1080p60" / f"{path.stem}.mp4"
        if output_path.exists():
            shutil.move(str(output_path), str(path))
            QMessageBox.information(self, "File Saved", "The video has been rendered successfully")
        else:
            QMessageBox.critical(self, "Error", "The video could not be rendered")
    
    def update_image(self):
        frame = self.scene.renderer.get_frame()
        qimage = ImageQt(Image.fromarray(frame))
        pixmap = QPixmap.fromImage(qimage) \
            .scaled(self.label.width(), self.label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(pixmap)
