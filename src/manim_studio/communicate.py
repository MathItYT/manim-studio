from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np


class Communicate(QObject):
    update_scene = pyqtSignal(str)
    update_image = pyqtSignal(np.ndarray)
    end_scene = pyqtSignal()
    alert = pyqtSignal(Exception)
    save_snippet = pyqtSignal(str)
    next_slide = pyqtSignal()
    add_slider_to_editor = pyqtSignal(str, str, str, str, str)
    add_color_widget_to_editor = pyqtSignal(str, np.ndarray)
