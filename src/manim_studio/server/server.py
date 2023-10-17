import socket
from PyQt6.QtCore import QThread

from manim_studio.communicate import Communicate


class Server(QThread):
    def __init__(self, host: str, port: int, password: str, communicate: Communicate, editor):
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.users: dict[str, socket.socket] = {}
        self.communicate = communicate
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()
        self.clients: list[socket.socket] = []
        self.threads: list[QThread] = []
        self.running = True
        self.editor = editor

    def run(self):
        while self.running:
            try:
                client, address = self.s.accept()
            except OSError:
                break
            thread = ClientThread(
                client, address, self.password, self.communicate, self.editor, self)
            thread.start()

    def disconnect_user(self, username: str):
        self.users[username].sendall(b"exit")
        del self.users[username]

    def close(self):
        self.running = False
        for client in self.clients:
            client.sendall(b"exit")
            client.close()
        for thread in self.threads:
            thread.quit()
            thread.wait()
        self.s.close()


class ClientThread(QThread):
    def __init__(self, client: socket.socket, address: tuple[str, int], password: str, communicate: Communicate, editor, main_thread: Server):
        super().__init__()
        self.client = client
        self.address = address
        self.password = password
        self.communicate = communicate
        self.editor = editor
        self.main_thread = main_thread

    def run(self):
        msg = self.guaranteed_recv()
        try:
            msg.decode("utf-8")
        except UnicodeDecodeError:
            self.client.sendall(b"Wrong password (UnicodeDecodeError)")
            self.client.close()
            return
        if msg.decode("utf-8") == self.password:
            self.main_thread.clients.append(self.client)
            self.client.sendall(b"Correct password")
            while True:
                msg = self.guaranteed_recv()
                if msg.decode("utf-8").startswith("username="):
                    user = msg.decode("utf-8").split("=")[1]
                    if user not in self.main_thread.users:
                        self.main_thread.users[user] = self.client
                        self.client.sendall(b"Username accepted")
                    else:
                        self.client.sendall(b"Username already taken")
                        continue
                    self.communicate.show_in_status_bar.emit(
                        f"{user} connected")
                    continue
                elif msg.decode("utf-8") == "get_controls":
                    self.communicate.add_controls_to_client.emit(
                        self.client, self.editor.controls)
                    continue
                elif msg.decode("utf-8") == "exit":
                    self.main_thread.disconnect_user(user)
                    break
                elif msg.decode("utf-8").startswith("set_slider_value"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, value)
                    continue
                elif msg.decode("utf-8").startswith("set_color"):
                    _, name, r, g, b, a = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, f"{r},{g},{b},{a}")
                    continue
                elif msg.decode("utf-8").startswith("set_dropdown"):
                    _, name, text = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, text)
                    continue
                elif msg.decode("utf-8").startswith("set_line_edit"):
                    _, name, *words = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, " ".join(words))
                    continue
                elif msg.decode("utf-8").startswith("set_text_edit"):
                    _, name, *words = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, " ".join(words))
                    continue
                elif msg.decode("utf-8").startswith("set_checkbox"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_control_value.emit(
                        name, value)
                    continue
                elif msg.decode("utf-8").startswith("button_clicked"):
                    _, name = msg.decode("utf-8").split(" ")
                    self.communicate.press_button.emit(name)
                    continue
                elif msg.decode("utf-8").startswith("set_position_control_value_x"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_position_control_x.emit(
                        name, value)
                    continue
                elif msg.decode("utf-8").startswith("set_position_control_value_y"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_position_control_y.emit(
                        name, value)
                    continue
                elif msg.decode("utf-8").startswith("set_position_control_value_z"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_position_control_z.emit(
                        name, value)
                    continue
                elif msg.decode("utf-8").startswith("set_position_control_display_dot"):
                    _, name, value = msg.decode("utf-8").split(" ")
                    self.communicate.set_position_control_display_dot.emit(
                        name, value)
                    continue
                else:
                    self.communicate.update_scene.emit(msg.decode("utf-8"))
        else:
            self.client.sendall(b"Wrong password")
            self.client.close()

    def guaranteed_recv(self):
        return self.client.recv(1024)
