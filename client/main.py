from PyQt6.QtWidgets import QApplication
from dialog import ClientDialog
from client import ManimStudioClient
import sys


def main():
    app = QApplication([])
    client_dialog = ClientDialog()
    client_dialog.exec()
    host, port, username, password = client_dialog.get_server_info()
    client = ManimStudioClient(host, port, username, password)
    client.show()
    if client.success:
        client.controls_dialog.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
