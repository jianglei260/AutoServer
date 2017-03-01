# coding=utf-8
import socket, threading, time
import json

host = "localhost"
upload_port = 8081
access_port = 8082
# status_data = None
BUFFER_SIZE = 1024


# upload_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# upload_server.bind((host, upload_port))
# upload_server.listen(1)
# upload_client, address = upload_server.accept()
# while (True):
#     status_data = upload_client.recv(BUFFER_SIZE)
#     if status_data:
#         print(str(status_data))

class AutoServer:
    def __init__(self):
        self.access_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.access_server.bind((host, access_port))
        self.access_server.listen(10)
        self.terminal_client = None

    def start_server(self):
        while (True):
            access_client, client_address = self.access_server.accept()
            thread = threading.Thread(target=self.handle_client, args=(access_client, client_address))
            thread.start()

    def handle_client(self, client, address):
        while (True):
            cmd = client.recv(BUFFER_SIZE)
            if not cmd:
                break
            self.handle_cmd(client, json.loads(cmd))

    def handle_cmd(self, client, cmd):
        cmd_type = cmd['type']
        cmd_value = cmd['value']
        if cmd_type == "cmd":
            # upload_client.sendall(cmd)
            print("redrect cmd:" + cmd_value)
            if self.terminal_client:
                self.terminal_client.sendall(cmd)
        elif cmd_type == "role":
            if cmd_value == "terminal":
                self.terminal_client = client
                print("connected terminal")


if __name__ == "__main__":
    auto_server=AutoServer()
    auto_server.start_server()