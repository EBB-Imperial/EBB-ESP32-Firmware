import socket

class TCPSender:
    def __init__(self, server_ip, server_port, socket = None, log_level = 0):
        self.server_ip = server_ip
        self.server_port = server_port
        self.log_level = log_level
        self.client_socket = socket

    def start(self):
        # if self.client_socket is None:
        #     self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.client_socket.connect((self.server_ip, self.server_port))
        if self.log_level > 0: print(f"Sender.py: Connected to server at {self.server_ip}:{self.server_port}")

    def send(self, message):
        message += '\n'
        self.client_socket.send(message.encode())
        if self.log_level > 0: print(f"Sender.py: Message sent to ESP32: {message}")

    def disconnect(self):
        try:
            self.client_socket.close()
            if self.log_level > 0: print(f"Disconnected from server")
        except Exception as e:
            ...

if __name__ == "__main__":
    server_ip = '192.168.4.1'  # Replace with your ESP32 IP address
    server_port = 1234  # Replace with your ESP32 server port

    tcp_sender = TCPSender(server_ip, server_port)
    tcp_sender.start()

    while True:
        message = input("Enter a message to send: ")
        tcp_sender.send(message)

        if message.lower() == 'quit':
            break

    tcp_sender.disconnect()
