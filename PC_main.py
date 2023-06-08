from PC_receiver_v1 import TCPReceiver
from PC_receiver_v2 import UDPReceiver
from PC_sender_v2 import UDPSender
from PC_input_simulator import UDPReceiverSimulator
from PC_image_decoder import ImageDecoder
from PC_websocket_client import WebSocketClient

import time

"""
    This is the main script that runs on the PC.
    It is responsible for:
        - receiving data from the URAT receiver (sensor data - to be used in sensor fusion)
        - do image decoding (from raw bytes to RGB image - done by ImageDecoder)
        - forward the decoded image to the image processing script (TODO)
        - forward the sensor data to the sensor fusion script (TODO)
        - send commands to the URAT transmitter (TODO)
"""

# ------------------- hyper parameters ------------------- #
LOG_LEVEL = 3

# image decoder
USE_SIM_INPUT = False
USE_SIM_UDP = False
SAVE_RECORD = False
DELETE_OLD_IMAGES = True
IMG_FOLDER = "images"
IMG_WIDTH = 320
IMG_HEIGHT = 235
SYNC_WORD = b"UUUUUUUUUUUUUUUw"

# URAT receiver
ESP_IP = "192.168.4.255"  # sending ip
ESP_PORT = 1234         # sending port
UDP_IP = "192.168.4.1"             # receiving ip (currently set to boardcast)
UDP_PORT = ESP_PORT     # receiving port

# websocket client
LOCAL_SERVER_URL = "ws://localhost:8080/"
# -------------------------------------------------------- #


def main():

    if USE_SIM_INPUT:
        receiver = UDPReceiverSimulator(ip=UDP_IP, port=UDP_PORT, log_level=LOG_LEVEL)
    else:
        receiver = TCPReceiver(ip=UDP_IP, port=UDP_PORT, log_level=LOG_LEVEL, record_mode=SAVE_RECORD)

    decoder = ImageDecoder(receiver, img_width=IMG_WIDTH, img_height=IMG_HEIGHT, img_folder=IMG_FOLDER,
                           sync_word=SYNC_WORD, use_sim_input=USE_SIM_INPUT, delete_old_images=DELETE_OLD_IMAGES,
                            log_level=LOG_LEVEL)
    
    sender = UDPSender(dst_ip=ESP_IP, dst_port=ESP_PORT, log_level=0, test_mode=USE_SIM_INPUT)

    socket_client = WebSocketClient(url=LOCAL_SERVER_URL, log_level=0)

    receiver.start()
    decoder.start()
    socket_client.start()

    # self test on UDP
    if USE_SIM_UDP:
        sender.self_test()


    try:
        # Main loop
        while True:
            # testing
            
            #sender.send_data(b"**data**")
            time.sleep(1)  # Pause for a while
            
    except KeyboardInterrupt:
        print("exiting...")

    # Clean up, stop the threads when done
    receiver.stop()
    socket_client.close()
    decoder.stop()
    


if __name__ == "__main__":
    main()