import socket
from PyQt6.QtCore import QThread

from manim_studio.communicate import Communicate


class Server(QThread):
    def __init__(self, host: str, port: int, password: str, communicate: Communicate):
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.communicate = communicate
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()
        self.clients: list[socket.socket] = []
        self.threads: list[QThread] = []
        self.running = True

    def run(self):
        while self.running:
            client, address = self.s.accept()
            self.clients.append(client)
            self.threads.append(ClientThread(
                client, address, self.password, self.communicate))
            self.threads[-1].start()

    def close(self):
        self.running = False
        for client in self.clients:
            client.send(b"exit")
            client.close()
        for thread in self.threads:
            thread.quit()
            thread.wait()
        self.s.close()


class ClientThread(QThread):
    def __init__(self, client: socket.socket, address: tuple[str, int], password: str, communicate: Communicate):
        super().__init__()
        self.client = client
        self.address = address
        self.password = password
        self.communicate = communicate

    def run(self):
        msg = self.client.recv(1024)
        try:
            msg.decode("utf-8")
        except UnicodeDecodeError:
            self.client.send(b"Wrong password (UnicodeDecodeError)")
            self.client.close()
            return
        if msg.decode("utf-8") == self.password:
            self.client.send(b"Correct password")
            while True:
                msg = self.client.recv(1024)
                if msg.decode("utf-8") == "exit":
                    break
                self.communicate.update_scene.emit(msg.decode("utf-8"))
                self.client.send(b"Code executed")
            self.client.send(b"exit")
            self.client.close()
        else:
            self.client.send(b"Wrong password")
            self.client.close()
