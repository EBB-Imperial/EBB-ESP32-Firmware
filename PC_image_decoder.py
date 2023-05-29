import time
import os
import PIL.Image as Image

from PC_receiver_v2 import UDPReceiver
from PC_input_simulator import UDPReceiverSimulator

IMG_WIDTH = 320
IMG_HEIGHT = 235

# Sync word: ASCII UUUUUUUUUUUUUUUw, i.e. ([0x55] * 15) + [0x77]
SYNC_WORD = b"UUUUUUUUUUUUUUUw"

IMG_FOLDER = "images"

USE_SIM_INPUT = True    # if set to true, use input stream from UDPReceiverSimulator

DELETE_OLD_IMAGES = True    # if set to true, delete all images in the image folder before starting

def rgb565_to_rgb888(data):
    r = (data & 0xF800) >> 11
    g = (data & 0x07E0) >> 5
    b = (data & 0x001F)
    return (min(r << 3, 255), min(g << 2, 255), min(b << 3, 255))


def process_byte(data):
    # convert from RGB565 to RGB888
    data = int.from_bytes(data, byteorder="little")
    data = rgb565_to_rgb888(data)

    return data


def pixels_to_image(pixels):
    # flatten list of tuples and convert it to bytes
    pixels = bytes([px for rgb in pixels for px in rgb])
    # print the length of the pixels
    print("pixels length: ", len(pixels), "expected length: ", IMG_WIDTH * IMG_HEIGHT * 3)
    # since we are using UDP, we might receive more or less data than expected.
    # we need to pad the data to the expected size
    pixels += bytes([0] * (IMG_WIDTH * IMG_HEIGHT * 3 - len(pixels)))
    if len(pixels) != IMG_WIDTH * IMG_HEIGHT * 3:
        # truncate the data if it is too long
        pixels = pixels[:IMG_WIDTH * IMG_HEIGHT * 3]
    
    return Image.frombytes("RGB", (IMG_WIDTH, IMG_HEIGHT), pixels)



def delete_old_images():
    for filename in os.listdir(IMG_FOLDER):
        file_path = os.path.join(IMG_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def save_image(img, filename):
    image_path = os.path.join(IMG_FOLDER, filename)
    # if file already exists, append a number to the filename
    if os.path.exists(image_path):
        i = 1
        while True:
            new_filename = filename.split(".")[0] + "_" + str(i) + "." + filename.split(".")[1]
            new_image_path = os.path.join(IMG_FOLDER, new_filename)
            if not os.path.exists(new_image_path):
                image_path = new_image_path
                break
            i += 1
    img.save(image_path)
    print("saved new image: " + image_path)


if __name__ == "__main__":

    if DELETE_OLD_IMAGES:
        delete_old_images()

    if USE_SIM_INPUT:
        receiver = UDPReceiverSimulator()
    else:
        receiver = UDPReceiver()
        receiver.start()

    data_stream = receiver.get_data_stream()

    raw_img_pixels = []

    for data in data_stream:
        #print("New data: ", data)

        # find the sync word
        sync_word_index = data.find(SYNC_WORD)

        # if the sync word is not found, append the data to the previous data
        if sync_word_index == -1:
            raw_img_pixels += data
            continue
    
        # if the sync word is found, append the data after the sync word to the previous data
        raw_img_pixels += data[sync_word_index + len(SYNC_WORD):]

        # each pixel is 2 bytes, we iterate and process 2 bytes at a time
        img_pixels = []
        print("raw_img_pixels length: ", len(raw_img_pixels), "expected length: ", IMG_WIDTH * IMG_HEIGHT * 2)
        for i in range(0, len(raw_img_pixels), 2):
            img_pixels.append(process_byte(raw_img_pixels[i:i+2]))
        print("img_pixels length: ", len(img_pixels), "expected length: ", IMG_WIDTH * IMG_HEIGHT * 3)
        print()
        
        # convert the pixels to an image
        img = pixels_to_image(img_pixels)

        # save the image, filename is the current timestamp
        save_image(img, str(int(time.time())) + ".jpg")

        # clear the raw image pixels
        raw_img_pixels = []


    # When you're done:
    receiver.stop()
