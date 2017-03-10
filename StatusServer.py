# coding=utf-8
import socket, threading, time
import json
import sys

host = ""
# upload_port = 8081
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
        self.status = None
        self.control_client = []

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
            cmds = cmd.split("\n")
            for command in cmds:
                if not command:
                    continue
                try:
                    json_cmd = json.loads(command)
                    self.handle_cmd(client, json_cmd, address)
                except:
                    print("error json" + command)

    def handle_cmd(self, client, cmd, address):
        print("redrect cmd:" + str(cmd))
        host = address[0]
        print(host)
        cmd_type = cmd['type']
        cmd_value = cmd['value']
        if cmd_type == "cmd":
            if self.terminal_client:
                self.terminal_client.send(json.dumps(cmd))
        elif cmd_type == "role":
            if cmd_value == "terminal":
                self.terminal_client = client
                if self.monitor:
                    thread = threading.Thread(target=self.monitor.connect_terminal, args=(address,))
                    thread.start()
                print("connected terminal")
            else:
                self.control_client.append(client)
                if self.monitor:
                    thread = threading.Thread(target=self.monitor.connect_client, args=(address,))
                    thread.start()
        elif cmd_type == "status":
            self.status = cmd_value
            self.redirect_status(json.dumps(cmd))

    def redirect_status(self, status):
        for client in self.control_client:
            if client:
                try:
                    client.send(status)
                    # print("send status:" + status)
                except:
                    pass

    def set_monitor(self, monitor):
        self.monitor = monitor;


monitor_port = 8083
client_monitor_port = 8084


class Monitor:
    def __init__(self):
        self.client = None
        self.terminal = None
        self.buffer = [];

    def connect_terminal(self, terminal_host):
        terminal_address = (terminal_host[0], monitor_port)
        if self.terminal:
            self.terminal.close()
        self.terminal = socket.create_connection(terminal_address, timeout=60000);

        while (True):
            self.buffer = self.terminal.recv(20000)
            if not self.buffer:
                break
            # received_buffer=""
            # received_buffer=received_buffer+self.buffer
            # data_len=struct.unpack("!5s",self.buffer)[0]
            # int_data_len=int(data_len)
            # print("should receive data" + str(int_data_len))
            # self.buffer=self.terminal.recv(int_data_len)
            # print("data type" + str(type(self.buffer)))
            # received=len(self.buffer);
            # received_buffer=received_buffer+self.buffer
            # while(received<int_data_len):
            #     self.buffer=self.terminal.recv(int_data_len-received)
            #     received=received+len(self.buffer);
            #     received_buffer=received_buffer+self.buffer
            #     print("received data" + str(received))
            # print("receive buffer data" + str(len(received_buffer)))
            if self.client and self.buffer:
                try:
                    self.client.sendall(self.buffer)
                except:
                    pass

    def connect_client(self, client_host):
        terminal_address = (client_host[0], client_monitor_port)
        if self.client:
            try:
                self.client.close()
            except:
                pass
        self.client = socket.create_connection(terminal_address, timeout=60000);


if __name__ == "__main__":
    auto_server = AutoServer()
    monitor = Monitor()
    auto_server.set_monitor(monitor)
    auto_server.start_server()
