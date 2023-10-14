import socket
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QStatusBar


class ManimStudioClient(QWidget):
    def __init__(self, host: str, port: int, password: str):
        super().__init__()
        self.setWindowTitle("Manim Studio Client")
        self.host = host
        self.port = port
        self.password = password
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send(self.password.encode("utf-8"))
        msg = self.s.recv(1024)
        if msg.decode("utf-8") == "Correct password":
            self.setLayout(QVBoxLayout())
            self.label = QLabel()
            self.label.setText(
                f"Connected to {self.host}:{self.port}")
            self.layout().addWidget(self.label)
            self.code_edit = QTextEdit()
            self.code_edit.setPlaceholderText("Enter the code")
            self.layout().addWidget(self.code_edit)
            self.send_button = QPushButton("Send (Ctrl+Return)")
            self.send_button.setShortcut("Ctrl+Return")
            self.send_button.clicked.connect(self.send_code)
            self.layout().addWidget(self.send_button)
            self.status_bar = QStatusBar()
            self.layout().addWidget(self.status_bar)
        else:
            QMessageBox.critical(
                self, "Error", msg.decode("utf-8"))
            self.close()

    def closeEvent(self, event):
        self.s.send(b"exit")
        self.s.close()
        super().closeEvent(event)

    def send_code(self):
        code = self.code_edit.toPlainText()
        self.s.send(code.encode("utf-8"))
        self.code_edit.clear()
        msg = self.s.recv(1024)
        self.status_bar.showMessage(msg.decode("utf-8"), msecs=5000)
