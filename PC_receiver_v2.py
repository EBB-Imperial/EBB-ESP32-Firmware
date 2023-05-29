import socket
from multiprocessing import Process, Queue, freeze_support

class UDPReceiver:
    def __init__(self, ip="", port=1234):
        self.ip = ip
        self.port = port
        self.queue = Queue()
        self.process = Process(target=self.run)

    def start(self):
        self.process.start()
        freeze_support()    # allow current process to finish bootstrapping

    def stop(self):
        self.process.terminate()

    def run(self):
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind((self.ip, self.port))

        while True:
            #print("receiving data: ", end="")
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
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
