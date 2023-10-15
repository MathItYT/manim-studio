from manim_studio.server.server import Server
from PyQt6.QtWidgets import QWidget, QInputDialog, QLabel, QVBoxLayout, QPushButton, QLineEdit
from pyngrok import ngrok


class ManimStudioServer(QWidget):
    def __init__(self, communicate, editor):
        super().__init__()
        self.setWindowTitle("Manim Studio Server")
        self.communicate = communicate
        password_dialog = QInputDialog()
        password_dialog.setLabelText("Create a password for the server: ")
        password_dialog.setWindowTitle("Manim Studio Server")
        password_dialog.setModal(True)
        password_dialog.exec()
        self.password = password_dialog.textValue()
        self.server = Server("", 5555, self.password, self.communicate, editor)
        self.server.start()
        self.label = QLabel()
        self.label.setText(
            f"Server started at {self.server.host}:{self.server.port}")
        self.ask_label = QLabel()
        self.ask_label.setText(
            "If you want to work collaboratively, you need to have installed ngrok.\nIf you click the button below, ngrok will be started and you will be able to share the link with your mates.")
        self.ask_label.setWordWrap(True)
        self.ask_label.setMargin(10)
        self.ask_label.setIndent(10)
        self.public_url = None
        self.ask_label.setStyleSheet("background-color: #f0f0f0;")
        self.button = QPushButton("Start ngrok")
        self.button.clicked.connect(self.start_ngrok)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.ask_label)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        editor.manim_studio_server = self.server

    def closeEvent(self, event):
        self.server.close()
        if self.public_url is not None:
            self.stop_ngrok()
        super().closeEvent(event)

    def start_ngrok(self):
        tunnel = ngrok.connect(5555, "tcp")
        self.button.setText("ngrok started")
        self.button.setEnabled(False)
        self.link_label = QLabel()
        self.link_label.setText(
            "ngrok started. You can share the host and port below with your mates.")
        self.link_label.setWordWrap(True)
        self.link_label.setMargin(10)
        self.link_label.setIndent(10)
        self.link_label.setStyleSheet("background-color: #f0f0f0;")
        self.layout.addWidget(self.link_label)
        self.link = QLineEdit()
        self.public_url = tunnel.public_url
        host, port = tunnel.public_url[6:].split(":")
        self.link.setText(f"HOST={host}; PORT={port}")
        self.link.setReadOnly(True)
        self.layout.addWidget(self.link)

    def stop_ngrok(self):
        ngrok.disconnect(self.public_url)
        ngrok.kill()
