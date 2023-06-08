import os
import io
import time
import math
from tqdm import tqdm

from PC_receiver_v2 import UDPReceiver, PictureData

RECORD_SIZE_LIMIT = 1024 * 512  # e.g. 0.5MB
RECORDED_DATA_PATH = "recorded_inputs/image_with_header.txt"
PACKAGE_SIM_DELAY = 0.01  # seconds

class UDPReceiverSimulator:
    def __init__(self, ip = "", port = 1234, log_level = 1, data_file_path = RECORDED_DATA_PATH, package_sim_delay = PACKAGE_SIM_DELAY, record_size_limit=RECORD_SIZE_LIMIT, record_mode=False):
        self.record_mode = record_mode
        if self.record_mode:
            self.receiver = UDPReceiver(ip, port, log_level=1)
        #self.receiver.start()
        self.data_file_path = data_file_path
        self.record_size_limit = record_size_limit
        self.package_sim_delay = package_sim_delay
        self.recorded_bytes = io.BytesIO()
        self.log_level = log_level

    def start(self):
        if self.record_mode:
            print("starting receiver in simulator.")
            self.receiver.start()

    def record(self):
        total_received = 0
        data_stream = self.receiver.get_raw_data_stream()
        pbar = tqdm(self.record_size_limit)
        for data in data_stream:
            print("1")
            total_received += len(data)
            self.recorded_bytes.write(data)
            pbar.update(len(data))
            if total_received >= self.record_size_limit:
                break
        self.recorded_bytes.seek(0)

    def save_recorded_data(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.recorded_bytes.getbuffer())
    

    def get_raw_data_stream(self, package_size=1027):
        with open(self.data_file_path, 'rb') as f:
            # this function is a generator. We return one package at a time
            while True:
                data = f.read(package_size)
                if not data:
                    break
                time.sleep(self.package_sim_delay)
                yield data
    
    def get_picture_data_stream(self, package_size=1027):
        with open(self.data_file_path, 'rb') as f:
            # this function is a generator. We return one package at a time
            picture_size = 320 * 236 * 2
            picture_count = 0
            packet_index = 0
            while True:
                data = f.read(package_size - 3)
        
                if not data:
                    break

                packet_index += (package_size - 3)

                if packet_index >= picture_size:
                    packet_index = 0
                    picture_count += 1

                data = PictureData(data, positionIndex=packet_index)
                
                time.sleep(self.package_sim_delay)
                yield data


    def stop(self):
        if self.record_mode:
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
    simulator = UDPReceiverSimulator(record_mode=True)
    simulator.start()
    simulator.record()
    simulator.save_recorded_data(RECORDED_DATA_PATH)
    # data = simulator.get_data_stream()
    # print(data)  # Do something with the loaded data
    simulator.stop()

    convert_recorded_data_to_readable(RECORDED_DATA_PATH)