from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent, QTabletEvent, QWheelEvent, QKeyEvent
from .communicate import Communicate
from manim import config, Mobject, ScreenRectangle, MovingCameraScene, ThreeDScene
from .render_thread import RenderThread
import numpy as np


def convert_to_manim_coords(x: int, y: int, label: QLabel, frame: ScreenRectangle | None = None) -> tuple[float, float]:
    w, h = label.width(), label.height()
    top_left = label.mapToGlobal(label.rect().topLeft())
    x -= top_left.x()
    y -= top_left.y()
    if frame is not None:
        frame_width, frame_height = frame.width, frame.height
        frame_center = frame.get_center()
    else:
        frame_width, frame_height = config.frame_width, config.frame_height
        frame_center = np.array([0, 0, 0])
    x = (x - w / 2) / w * frame_width + frame_center[0]
    y = (h / 2 - y) / h * frame_height + frame_center[1]
    return x, y


class PreviewWidget(QWidget):
    def __init__(self, communicate: Communicate, screen_size: tuple[int, int], render_thread: RenderThread):
        super().__init__()
        self.setWindowTitle("Preview")
        self.communicate = communicate
        self.mouse_coords = None
        self.w, self.h = screen_size
        self.interactive_mobjects: dict[str, Mobject] = {}
        self.communicate.update_image.connect(self.update_image)
        self.communicate.enable_interact.connect(self.enable_interact)
        self.communicate.add_to_interactive_mobjects.connect(
            self.add_to_interactive_mobjects)
        self.communicate.remove_from_interactive_mobjects.connect(
            self.remove_from_interactive_mobjects)
        self.render_thread = render_thread
        self.enable = False
        self.scene = self.render_thread.scene
        self.init_ui()
        self.setMouseTracking(True)
        self.preview_label.setMouseTracking(True)

    def add_to_interactive_mobjects(self, name: str):
        if name in self.interactive_mobjects:
            return
        self.interactive_mobjects[name] = getattr(self.scene, name)

    def remove_from_interactive_mobjects(self, name: str):
        if name not in self.interactive_mobjects:
            return
        del self.interactive_mobjects[name]

    def enable_interact(self, enable: bool):
        self.enable = enable
        if not hasattr(self.scene, "drawings"):
            self.communicate.update_scene.emit(
                "self.drawings = VGroup(VMobject().make_smooth())\nself.add(self.drawings)")

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.enable or isinstance(self.scene, ThreeDScene):
            return
        pos = event.pos()
        x, y = pos.x(), pos.y()
        if not isinstance(self.scene, MovingCameraScene):
            x, y = convert_to_manim_coords(x, y, self.preview_label)
        elif isinstance(self.scene, MovingCameraScene):
            x, y = convert_to_manim_coords(x, y, self.preview_label, self.scene.camera.frame)
        self.mouse_coords = x, y
        if event.buttons() != Qt.MouseButton.LeftButton:
            return
        for name, mobject in self.interactive_mobjects.items():
            center, width, height = mobject.get_center(), mobject.width, mobject.height
            if center[0] - width / 2 <= x <= center[0] + width / 2 and center[1] - height / 2 <= y <= center[1] + height / 2:
                self.communicate.update_scene.emit(f"getattr(self, {name.__repr__()}).move_to(np.array([{x}, {y}, 0]))")
                break

    def mousePressEvent(self, event: QMouseEvent):
        if not self.enable or isinstance(self.scene, ThreeDScene):
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.communicate.update_scene.emit(
                "if self.drawings.submobjects: self.drawings.submobjects.pop()\nif not self.drawings.submobjects: self.drawings.add(VMobject().make_smooth())")
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self.communicate.update_scene.emit(
                "self.drawings.submobjects.clear()\nself.drawings.add(VMobject().make_smooth())")
            return

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.init_preview_label()
        self.render_thread.start()

    def init_preview_label(self):
        self.preview_label = QLabel()
        w, h = config.pixel_width, config.pixel_height
        aspect_ratio = w / h
        h = min(h, self.h)
        w = int(h * aspect_ratio)
        w = min(w, self.w)
        h = int(w / aspect_ratio)
        self.preview_label.setFixedSize(w, h)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setGeometry(0, 0, w, h)
        self.w = w
        self.h = h
        self.layout().addWidget(self.preview_label)
    
    def wheelEvent(self, event: QWheelEvent):
        if not self.enable or not isinstance(self.scene, MovingCameraScene) or isinstance(self.scene, ThreeDScene):
            return
        delta = event.angleDelta().y()
        mouse_pos = event.position()
        if isinstance(self.scene, MovingCameraScene):
            x, y = mouse_pos.x(), mouse_pos.y()
            x, y = convert_to_manim_coords(x, y, self.preview_label, self.scene.camera.frame)
            self.communicate.update_scene.emit(
                f"self.camera.frame.scale(1 - {delta / 1000}).move_to(np.array([{x}, {y}, 0]))")
    
    def keyPressEvent(self, event: QKeyEvent):
        if not self.enable or isinstance(self.scene, ThreeDScene):
            return
        key = event.key()
        if key == Qt.Key.Key_R and isinstance(self.scene, MovingCameraScene):
            self.communicate.update_scene.emit(
                "self.camera.frame.scale_to_fit_height(config.frame_height).move_to(np.array([0, 0, 0]))")
        if key == Qt.Key.Key_H:
            x, y = self.mouse_coords
            for name, mobject in self.interactive_mobjects.items():
                center, width, height = mobject.get_center(), mobject.width, mobject.height
                if center[0] - width / 2 <= x <= center[0] + width / 2 and center[1] - height / 2 <= y <= center[1] + height / 2:
                    self.communicate.update_scene.emit(f"self.play(Indicate(getattr(self, {name.__repr__()})))")
                    break
        if key == Qt.Key.Key_C:
            x, y = self.mouse_coords
            for name, mobject in self.interactive_mobjects.items():
                center, width, height = mobject.get_center(), mobject.width, mobject.height
                if center[0] - width / 2 <= x <= center[0] + width / 2 and center[1] - height / 2 <= y <= center[1] + height / 2:
                    self.communicate.update_scene.emit(f"self.play(Circumscribe(getattr(self, {name.__repr__()})))")
                    break
    
    def tabletEvent(self, event: QTabletEvent):
        if not self.enable or isinstance(self.scene, ThreeDScene):
            return
        pos = event.position()
        x, y = pos.x(), pos.y()
        if not isinstance(self.scene, MovingCameraScene):
            x, y = convert_to_manim_coords(x, y, self.preview_label)
        elif isinstance(self.scene, MovingCameraScene):
            x, y = convert_to_manim_coords(x, y, self.preview_label, self.scene.camera.frame)
        if event.pressure() > 0:
            self.communicate.update_scene.emit(
                f"""
if self.drawings[-1].has_no_points():
    self.drawings[-1].start_new_path(np.array([{x}, {y}, 0]))
else:
    self.drawings[-1].add_line_to(np.array([{x}, {y}, 0]))
""".strip())
        else:
            self.communicate.update_scene.emit(
                f"self.drawings.add(VMobject().make_smooth())")

    def update_image(self, image: np.ndarray):
        self.preview_label.setPixmap(QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGBA8888)).scaledToHeight(self.h, Qt.TransformationMode.SmoothTransformation))
