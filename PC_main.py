from PC_receiver_v3 import TCPReceiver
from PC_sender_v3 import TCPSender
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
AUTO_TEST_INSTRUCTION = False
SAVE_RECORD = False
DELETE_OLD_IMAGES = True
IMG_FOLDER = "images"
IMG_WIDTH = 320
IMG_HEIGHT = 235
SYNC_WORD = b"UUUUUUUUUUUUUUUw"

# URAT receiver
ESP_IP = "192.168.4.1"  # sending ip
ESP_PORT = 1234         # sending port
TCP_IP = "192.168.4.1"  # receiving ip
TCP_PORT = ESP_PORT     # receiving port

# websocket client
LOCAL_SERVER_URL = "ws://localhost:8080/"

# esp32 instructions
# sending data
SEND_IMAGE = "SEND_IMAGE"
SEND_SENSOR_DATA = "SEND_SENSOR_DATA"
# move command
MOVE = "MOVE"
ROTATE = "ROTATE"
# query state
QUERY_STATE = "QUERY_STATE"
# -------------------------------------------------------- #


def main():

    if USE_SIM_INPUT:
        receiver = UDPReceiverSimulator(ip=TCP_IP, port=TCP_PORT, log_level=LOG_LEVEL)
    else:
        receiver = TCPReceiver(ip=TCP_IP, port=TCP_PORT, log_level=LOG_LEVEL, record_mode=SAVE_RECORD)

    decoder = ImageDecoder(receiver, img_width=IMG_WIDTH, img_height=IMG_HEIGHT, img_folder=IMG_FOLDER,
                           use_sim_input=USE_SIM_INPUT, delete_old_images=DELETE_OLD_IMAGES,
                            log_level=LOG_LEVEL)

    receiver.start()
    decoder.start()

    sender = TCPSender(server_ip=ESP_IP, server_port=ESP_PORT, socket=receiver.socket, log_level=LOG_LEVEL)
    sender.start()

    socket_client = WebSocketClient(url=LOCAL_SERVER_URL, sender=sender, log_level=3)
    socket_client.start()

    sender.send(QUERY_STATE)

    try:
        # Main loop
        while True:
            for esp_data in receiver.get_esp_status_stream():
                if esp_data.ready:
                    if LOG_LEVEL > 0:
                        print("main.py: received READY message from ESP")
                    if AUTO_TEST_INSTRUCTION: sender.send(SEND_IMAGE)
                elif esp_data.image_sent:
                    # TODO: call image processing script
                    # for testing purpose, we send a random move instruction (e.g. MOVE:1 or ROTATE:10)
                    if LOG_LEVEL > 0:
                        print("main.py: received IMAGE_SENT message from ESP")
                    if AUTO_TEST_INSTRUCTION: 
                        random_move_val = str(int(time.time() * 1000) % 100)
                        sender.send(MOVE + ":" + random_move_val)
                else:
                    # if for some reason the ESP is not ready, we keep sending the query state message
                    time.sleep(0.1)
                    if AUTO_TEST_INSTRUCTION: 
                        sender.send(QUERY_STATE)
            
    except KeyboardInterrupt:
        print("exiting...")

    # Clean up, stop the threads when done
    receiver.stop()
    socket_client.close()
    decoder.stop()
    


if __name__ == "__main__":
    main()