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
            
    def self_test(self):
        # do a self test that uses the simulator to send picture data, boardcast to the local network
        from PC_input_simulator import UDPReceiverSimulator
        receiver = UDPReceiverSimulator(ip="192.168.1.10", port=1234, log_level=0, data_file_path="recorded_inputs/one_image_data_bytes.txt", package_sim_delay=0.1)
        receiver.start()
        sender = UDPSender(dst_ip="192.168.1.255", dst_port=1234, log_level=0, test_mode=False)
        for data in receiver.get_data_stream():
            sender.send_data(data)
        receiver.stop()
        print("UDPSender: self test finished.")


if __name__ == "__main__":
    # # Test the UDPSender
    # sender = UDPSender()
    # data = b"Hello, world!"  # Sample data to send
    # sender.send_data(data)
    # print("UDPSender: Data sent.")

    

    ...
