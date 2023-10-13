import socket
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QMessageBox


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
            self.label = QLabel()
            self.label.setText(
                f"Connected to {self.host}:{self.port}")
            self.layout = QVBoxLayout()
            self.layout.addWidget(self.label)
            self.code_edit = QTextEdit()
            self.code_edit.setPlaceholderText("Enter the code")
            self.layout.addWidget(self.code_edit)
            self.send_button = QPushButton("Send")
            self.send_button.clicked.connect(self.send_code)
            self.layout.addWidget(self.send_button)
            self.setLayout(self.layout)
        else:
            QMessageBox.information(
                self, "Debug", msg.decode("utf-8"))
            self.close()

    def closeEvent(self, event):
        self.s.send(b"exit")
        self.s.close()
        super().closeEvent(event)

    def send_code(self):
        code = self.code_edit.toPlainText()
        self.s.send(code.encode("utf-8"))
        msg = self.s.recv(1024)
        if msg.decode("utf-8") == "Code executed":
            QMessageBox.information(
                self, "Code executed", "The code has been executed.")
        else:
            QMessageBox.critical(
                self, "Error", "The code could not be executed. Please try again.")
