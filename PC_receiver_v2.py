import socket
import time

UDP_IP = ""
UDP_PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

start_time = time.time()
total_bytes = 0

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    total_bytes += len(data)

    elapsed_time = time.time() - start_time
    if elapsed_time > 0: # to prevent division by zero
        transfer_rate = total_bytes / elapsed_time / 1024 # kbytes per second
        print("\rTransfer rate: {:.2f} kbps".format(transfer_rate), end="")
