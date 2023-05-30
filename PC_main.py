
from PC_receiver_v2 import UDPReceiver
from PC_input_simulator import UDPReceiverSimulator
from PC_image_decoder import ImageDecoder

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
USE_SIM_INPUT = True
DELETE_OLD_IMAGES = True
IMG_FOLDER = "images"
IMG_WIDTH = 320
IMG_HEIGHT = 235
SYNC_WORD = b"UUUUUUUUUUUUUUUw"
LOG_LEVEL = 1

ESP_IP = ""
ESP_PORT = 1234
# -------------------------------------------------------- #


def main():

    if USE_SIM_INPUT:
        receiver = UDPReceiverSimulator(ip=ESP_IP, port=ESP_PORT)
    else:
        receiver = UDPReceiver(ip=ESP_IP, port=ESP_PORT)

    decoder = ImageDecoder(receiver, img_width=IMG_WIDTH, img_height=IMG_HEIGHT, img_folder=IMG_FOLDER,
                           sync_word=SYNC_WORD, use_sim_input=USE_SIM_INPUT, delete_old_images=DELETE_OLD_IMAGES,
                            log_level=LOG_LEVEL)

    receiver.start()
    decoder.start()

    print("URAT receiver initilized.")

    # send command: receiver.send_data(b"**data**")

    # Main loop
    while True:
        # testing
        receiver.send_data(b"**data**")
        time.sleep(1)  # Pause for a while

    # Clean up, stop the threads when done
    receiver.stop()
    decoder.stop()