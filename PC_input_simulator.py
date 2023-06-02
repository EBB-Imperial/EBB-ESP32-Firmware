import os
import io
import time

from PC_receiver_v2 import UDPReceiver

RECORD_SIZE_LIMIT = 1024 * 1024  # e.g. 1MB
RECORDED_DATA_PATH = "recorded_inputs/recorded_bytes.txt"
PACKAGE_SIM_DELAY = 0.01  # seconds

class UDPReceiverSimulator:
    def __init__(self, ip = "", port = 1024, log_level = 1, package_sim_delay = PACKAGE_SIM_DELAY, record_size_limit=RECORD_SIZE_LIMIT):
        self.receiver = UDPReceiver(ip, port)
        #self.receiver.start()
        self.record_size_limit = record_size_limit
        self.package_sim_delay = package_sim_delay
        self.recorded_bytes = io.BytesIO()
        self.log_level = log_level

    def start(self):
        self.receiver.start()

    def record(self):
        total_received = 0
        data_stream = self.receiver.get_data_stream()
        for data in data_stream:
            total_received += len(data)
            self.recorded_bytes.write(data)
            if total_received >= self.record_size_limit:
                break
        self.recorded_bytes.seek(0)

    def save_recorded_data(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.recorded_bytes.getbuffer())
    

    def get_data_stream(self, package_size=1024):
        with open(RECORDED_DATA_PATH, 'rb') as f:
            # this function is a generator. We return one package at a time
            while True:
                data = f.read(package_size)
                if not data:
                    break
                time.sleep(self.package_sim_delay)
                yield data

    def stop(self):
        self.receiver.stop()

    def send_data(self, data):
        # just print data back, since it is a simulator
        if self.log_level > 0:
            print("input simulator: outputting data: ", end="")
            print(data)



def convert_recorded_data_to_readable(filename):
        with open(filename, 'rb') as f:
            data = f.read()
        with open(filename + "_pretty", 'w') as f:
            f.write(" ".join([hex(byte) for byte in data]))



if __name__ == "__main__":
    # simulator = UDPReceiverSimulator()
    # simulator.start()
    # simulator.record()
    # simulator.save_recorded_data(RECORDED_DATA_PATH)
    # # data = simulator.get_data_stream()
    # # print(data)  # Do something with the loaded data
    # simulator.stop()

    convert_recorded_data_to_readable(RECORDED_DATA_PATH)