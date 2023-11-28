from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import Qt


class ClientDialog(QDialog):
    """A dialog to connect to a Manim Studio server."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manim Studio Client Dialog")
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("Enter the host")
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("Enter the port")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter the password")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.host_edit)
        self.layout.addWidget(self.port_edit)
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(self.password_edit)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        self.setLayout(self.layout)

    def get_server_info(self):
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        username = self.username_edit.text()
        password = self.password_edit.text()
        return host, port, username, password
