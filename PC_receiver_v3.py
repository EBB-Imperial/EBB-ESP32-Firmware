import socket
from multiprocessing import Process, Queue, freeze_support
from PC_message_decoder import MessageDecoder, PictureData, ESP_StatusData

record_file_dir = "recorded_inputs/received_info_debug.txt"

class TCPReceiver:
    def __init__(self, ip="192.168.4.1", port=1234, socket = None, log_level = 1, record_mode=False):
        self.ip = ip
        self.port = port
        self.__queue = Queue()
        self.picture_data_queue = Queue()
        self.esp_status_queue = Queue()
        self.process = Process(target=self.run)
        self.socket = socket
        self.log_level = log_level
        self.record_mode = record_mode
        # decoder for decoding the received data
        self.decoder = MessageDecoder()

    def start(self):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
        self.process.start()
        if (self.log_level > 0): print("receiver.py: TCP process started.")
        freeze_support()    # allow current process to finish bootstrapping

    def stop(self):
        if (self.log_level > 0): print("receiver.py: stopping process...")
        self.process.terminate()
        if (self.log_level): print("receiver.py: process terminated.")
        try:
            self.socket.close()
        except Exception as e:
            ...

    def run(self):

        if self.log_level > 0: print("TCP receiver running.")

        buffer = bytes()

        # write the data to another file
        with open(record_file_dir, 'w') as f:
            while True:
                data = self.socket.recv(1024) # buffer size is 1024 bytes
                buffer += data

                while len(buffer) >= 8:  # while we have enough data for at least one message
                    message = buffer[:8]  # get the first 2 bytes
                    buffer = buffer[8:]  # remove the first 2 bytes from the buffer
                
                    decoded_data = self.decoder.decode_package(message)
                
                    self.__queue.put(message)
                    if self.record_mode:
                        f.writelines(hex(x) + "\n" for x in data)

                    if type(decoded_data) is PictureData:
                        self.picture_data_queue.put(decoded_data)

                    elif type(decoded_data) is ESP_StatusData:
                        self.esp_status_queue.put(decoded_data)

                    else:
                        print("Package type not matched by decoder: ", decoded_data)


    def get_raw_data_stream(self):
        while True:
            while not self.__queue.empty():
                yield self.__queue.get()

    
    def get_picture_data_stream(self):
        while True:
            while not self.picture_data_queue.empty():
                yield self.picture_data_queue.get()
    
    def get_esp_status_stream(self):
        while True:
            while not self.esp_status_queue.empty():
                yield self.esp_status_queue.get()


if __name__ == "__main__":
    # for testing use
    receiver = TCPReceiver()
    receiver.start()

    print("TCP receiver initilized.")

    # Keep the script running until the user terminates it
    for data in receiver.get_raw_data_stream():
        print("New data: ", data)
