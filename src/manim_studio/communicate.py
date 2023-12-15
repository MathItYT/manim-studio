from PyQt6.QtCore import pyqtSignal, QObject
from manim import Mobject
import numpy as np


class Communicate(QObject):
    """A class to communicate using signals and slots."""

    update_scene = pyqtSignal(str)
    update_image = pyqtSignal(np.ndarray)
    show_in_status_bar = pyqtSignal(str)
    print_gui = pyqtSignal(str)
    save_to_python = pyqtSignal()
    save_state = pyqtSignal()
    undo_state = pyqtSignal(bool)
    redo_state = pyqtSignal()
    update_state = pyqtSignal()
    add_value_tracker = pyqtSignal(str, Mobject)
    save_mobject = pyqtSignal()
    load_mobject = pyqtSignal()
    enable_interact = pyqtSignal(bool)
    add_to_interactive_mobjects = pyqtSignal(str)
    remove_from_interactive_mobjects = pyqtSignal(str)
    add_slider = pyqtSignal(str, int, int, int, int)
    add_text_box = pyqtSignal(str)
    add_line_box = pyqtSignal(str)
    add_color_picker = pyqtSignal(str)
    add_dropdown = pyqtSignal(str, list)
    add_checkbox = pyqtSignal(str, bool)
    add_spin_box = pyqtSignal(str, float, float, float)
    add_file_selector = pyqtSignal(str)
    add_position_control = pyqtSignal(str, float, float, float)
    add_button = pyqtSignal(str, str, str)
