import socket
from multiprocessing import Process, Queue, freeze_support
from PC_message_decoder import MessageDecoder, PictureData

record_file_dir = "recorded_inputs/received_info_debug.txt"


class UDPReceiver:
    def __init__(self, ip="", port=1234, log_level = 1, record_mode=False):
        self.ip = ip
        self.port = port
        self.__queue = Queue(maxsize=2048)
        self.picture_data_queue = Queue(maxsize=2048)
        self.process = Process(target=self.run)
        self.socket = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM)
        self.log_level = log_level
        self.record_mode = record_mode
        # decoder for decoding the received data
        self.decoder = MessageDecoder()

    def start(self):
        self.process.start()
        if (self.log_level > 0): print("receiver.py: URAT process started.")
        freeze_support()    # allow current process to finish bootstrapping

    def stop(self):
        if (self.log_level > 0): print("receiver.py: stopping process...")
        self.process.terminate()
        if (self.log_level): print("receiver.py: process terminated.")

    def run(self):
        self.socket.bind((self.ip, self.port))

        if self.log_level > 0: print("UDP receiver running.")

        # write the data to another file
        with open(record_file_dir, 'w') as f:
            while True:
                #print("receiving data: ", end="")
                data, addr = self.socket.recvfrom(1027) # buffer size is 1027 bytes
                #print(bin(int.from_bytes(data, "little")))
                self.__queue.put(data)
                if self.record_mode:
                    f.writelines(hex(x) + "\n" for x in data)
                
                # decode the data
                decoded_data = self.decoder.decode_package(data)

                if type(decoded_data) is PictureData:
                    self.picture_data_queue.put(decoded_data)
                
                else:
                    print("Package type not matched - got header: " + str(self.decoder.get_package_header(data)))


    def get_raw_data_stream(self):
        while True:
            while not self.__queue.empty():
                yield self.__queue.get()

    
    def get_picture_data_stream(self):
        while True:
            while not self.picture_data_queue.empty():
                yield self.picture_data_queue.get()

    
    


if __name__ == "__main__":

    # for testing use
    receiver = UDPReceiver()
    receiver.start()

    print("URAT receiver initilized.")

    # Keep the script running until the user terminates it
    for data in receiver.get_raw_data_stream():
        print("New data: ", data)
