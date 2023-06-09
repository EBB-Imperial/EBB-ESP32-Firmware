import time
import os
import PIL.Image as Image
from threading import Thread
from tqdm import tqdm

class ImageDecoder:

    def __init__(self, receiver, img_width=320, img_height=236, img_folder="images",
                use_sim_input=False, delete_old_images=True, log_level=1):

        self.IMG_WIDTH = img_width
        self.IMG_HEIGHT = img_height
        self.IMG_FOLDER = img_folder
        self.USE_SIM_INPUT = use_sim_input
        self.DELETE_OLD_IMAGES = delete_old_images
        self.LOG_LEVEL = log_level

        if self.DELETE_OLD_IMAGES:
            self.delete_old_images()

        self.receiver = receiver
        self.data_stream = self.receiver.get_picture_data_stream()

        self.thread = Thread(target=self.start_decode)
        self.is_stopped = False

        self.expected_raw_length = self.IMG_WIDTH * self.IMG_HEIGHT * 2
        self.expected_decoded_length = self.IMG_WIDTH * self.IMG_HEIGHT * 3

    def start(self):
        self.thread.start()

    @staticmethod
    def rgb565_to_rgb888(data):
        r = (data & 0xF800) >> 11
        g = (data & 0x07E0) >> 5
        b = (data & 0x001F)
        return (min(r << 3, 255), min(g << 2, 255), min(b << 3, 255))

    @staticmethod
    def process_byte(data):
        data = int.from_bytes(data, byteorder="little")
        return ImageDecoder.rgb565_to_rgb888(data)

    def pixels_to_image(self, pixels):
        pixels = bytes([px for rgb in pixels for px in rgb])
        if self.LOG_LEVEL > 2:
            print("image decoder: expected length: " + str(self.expected_decoded_length) + ", actual length: " + str(len(pixels)))
        pixels += bytes([0] * (self.expected_decoded_length - len(pixels)))
        if len(pixels) != self.expected_decoded_length:
            pixels = pixels[:self.expected_decoded_length]
        return Image.frombytes("RGB", (self.IMG_WIDTH, self.IMG_HEIGHT), pixels)

    def delete_old_images(self):
        for filename in os.listdir(self.IMG_FOLDER):
            file_path = os.path.join(self.IMG_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def save_image(self, img, filename):
        image_path = os.path.join(self.IMG_FOLDER, filename)
        if os.path.exists(image_path):
            i = 1
            while True:
                new_filename = filename.split(".")[0] + "_" + str(i) + "." + filename.split(".")[1]
                new_image_path = os.path.join(self.IMG_FOLDER, new_filename)
                if not os.path.exists(new_image_path):
                    image_path = new_image_path
                    break
                i += 1
        img.save(image_path)
        if self.LOG_LEVEL > 0:
            print("image decoder: saved new image: " + image_path)


    def start_decode(self):
        raw_img_pixels = []
        pbar = None
        image_started = False

        if self.LOG_LEVEL > 1: 
            print()
            pbar = tqdm(total=self.expected_raw_length)  # Start a new progress bar for the next image
            
        for picture_data in self.data_stream:

            if self.is_stopped:
                break

            data = picture_data.data
            abort = picture_data.abort
            finished = picture_data.finished
            start = picture_data.start

            if abort or finished:
                if abort:
                    if self.LOG_LEVEL > 0:
                        print("image decoder: image aborted")
                if finished:
                    if self.LOG_LEVEL > 0:
                        img_pixels = [self.process_byte(raw_img_pixels[i:i+2]) for i in range(0, len(raw_img_pixels), 2)]
                        img = self.pixels_to_image(img_pixels)
                        self.save_image(img, str(int(time.time())) + ".png")
                
                raw_img_pixels = []
                image_started = False

                if pbar is not None:
                    pbar.close()  # Close the current progress bar
                    print()
                    pbar = tqdm(total=self.expected_raw_length)  # Start a new progress bar for the next image
                continue

            # reject all data before the start message
            if not image_started:
                if start:
                    if self.LOG_LEVEL > 0:
                        print("image decoder: image started")
                    image_started = True

                continue


            if self.LOG_LEVEL > 1 and pbar is not None and data is not None:
                pbar.update(len(data))  # Update the progress bar for the last part of the current image

            # add the data to the raw image pixels
            raw_img_pixels += data
    

    def stop(self):
        self.is_stopped = True
        if self.LOG_LEVEL > 0:
            print("image decoder: stopping thread...")
        self.thread.join(1)
        if self.thread.is_alive:
            # force exit
            if self.LOG_LEVEL > 0:
                print("image decoder: thread terminated.")
                print("image decoder: forcing thread to terminate.")
            # doesn't work really, since the thread is blocked by the socket
            exit(1)
        if self.LOG_LEVEL > 0:
            print("image decoder: thread terminated.")
