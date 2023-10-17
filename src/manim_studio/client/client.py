import socket
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QStatusBar
from .control_dialog import ClientControls
from manim_studio.code_edit import CodeEdit


class ManimStudioClient(QWidget):
    def __init__(self, host: str, port: int, username: str, password: str):
        super().__init__()
        self.setWindowTitle("Manim Studio Client")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.sendall(self.password.encode("utf-8"))
        msg = self.s.recv(1024)
        if msg.decode("utf-8") == "Correct password":
            self.s.sendall(f"username={self.username}".encode("utf-8"))
            answer = self.s.recv(1024)
            if answer.decode("utf-8") == "Username already taken":
                QMessageBox.critical(
                    self, "Error", "Username already taken")
                self.close()
                self.success = False
                return
            else:
                self.success = True
            self.setLayout(QVBoxLayout())
            self.label = QLabel()
            self.label.setText(
                f"Connected to {self.host}:{self.port}")
            self.layout().addWidget(self.label)
            self.code_edit_label = QLabel("Code:")
            self.code_edit = CodeEdit()
            self.layout().addWidget(self.code_edit_label)
            self.layout().addWidget(self.code_edit)
            self.send_button = QPushButton("Send (Ctrl+Return)")
            self.send_button.setShortcut("Ctrl+Return")
            self.send_button.clicked.connect(self.send_code)
            self.layout().addWidget(self.send_button)
            self.status_bar = QStatusBar()
            self.layout().addWidget(self.status_bar)
            self.controls_dialog = ClientControls(self, self.s)
        else:
            QMessageBox.critical(
                self, "Error", msg.decode("utf-8"))
            self.close()

    def closeEvent(self, event):
        self.s.sendall(b"exit")
        self.s.close()
        super().closeEvent(event)

    def send_code(self):
        code = self.code_edit.text()
        self.s.sendall(code.encode("utf-8"))
        self.code_edit.clear()
        self.status_bar.showMessage("Code sent")
