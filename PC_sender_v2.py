import socket

class UDPSender:
    def __init__(self, dst_ip="192.168.4.1", dst_port=1234, log_level=1, test_mode=False):
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.log_level = log_level
        self.test_mode = test_mode

    def send_data(self, data):
        if self.test_mode:
            if self.log_level > 0:
                print(f"UDPSender(test mode): data " + str(data) + " sent to " + self.dst_ip + ":" + str(self.dst_port))
        
        else:
            self.socket.sendto(data, (self.dst_ip, self.dst_port))
            if self.log_level > 0:
                print(f"UDPSender: data " + str(data) + " sent to " + self.dst_ip + ":" + str(self.dst_port))


if __name__ == "__main__":
    # Test the UDPSender
    sender = UDPSender()
    data = b"Hello, world!"  # Sample data to send
    sender.send_data(data)
    print("UDPSender: Data sent.")
