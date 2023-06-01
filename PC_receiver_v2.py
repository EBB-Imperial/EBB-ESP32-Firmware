import socket
from multiprocessing import Process, Queue, freeze_support

class UDPReceiver:
    def __init__(self, ip="", port=1234, log_level = 1):
        self.ip = ip
        self.port = port
        self.queue = Queue()
        self.process = Process(target=self.run)
        self.socket = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM)
        self.log_level = log_level

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

        while True:
            #print("receiving data: ", end="")
            data, addr = self.socket.recvfrom(1024) # buffer size is 1024 bytes
            #print(data)
            self.queue.put(data)

    def get_data_stream(self):
        while True:
            while not self.queue.empty():
                yield self.queue.get()


if __name__ == "__main__":

    # for testing use
    receiver = UDPReceiver()
    receiver.start()

    print("URAT receiver initilized.")

    # Keep the script running until the user terminates it
    for data in receiver.get_data_stream():
        print("New data: ", data)
