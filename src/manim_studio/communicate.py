from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np
import socket


class Communicate(QObject):
    update_scene = pyqtSignal(str)
    update_image = pyqtSignal(np.ndarray)
    end_scene = pyqtSignal()
    alert = pyqtSignal(Exception)
    save_snippet = pyqtSignal(str)
    next_slide = pyqtSignal()
    add_slider_to_editor = pyqtSignal(str, str, str, str, str)
    add_color_widget_to_editor = pyqtSignal(str, np.ndarray)
    add_dropdown_to_editor = pyqtSignal(str, list, str)
    add_line_edit_to_editor = pyqtSignal(str, str)
    add_text_editor_to_editor = pyqtSignal(str, str)
    add_checkbox_to_editor = pyqtSignal(str, bool)
    add_button_to_editor = pyqtSignal(str, str)
    save_mobject = pyqtSignal()
    load_mobject = pyqtSignal()
    set_control_value = pyqtSignal(str, str)
    add_controls_to_client = pyqtSignal(socket.socket, dict)
    add_controls_to_clients = pyqtSignal(list, dict)
    press_button = pyqtSignal(str)
