
class PictureData:
    def __init__(self, data, positionIndex, abort, finished, start = False) -> None:
        self.data = data
        self.positionIndex = positionIndex
        self.abort = abort
        self.finished = finished
        self.start = start


class ESP_StatusData:
    def __init__(self, initialized = False, ready = False, image_sent = False) -> None:
        self.initialized = initialized
        self.ready = ready
        self.image_sent = image_sent


class MessageDecoder:
    def __init__(self) -> None:
        pass

    def decode_package(self, data):
        data_int = int.from_bytes(data, byteorder='little')

        # image data
        if data_int == 0x2727282829292A2A:
            print("received start message: " + str(data_int))
            return PictureData(None, None, False, False, True)
        elif data_int == 0x4747484849494A4A:
            print("received abort message: " + str(data_int))
            return PictureData(None, None, True, False)
        elif data_int == 0x6767686869696A6A:
            print("received finished message: " + str(data_int))
            return PictureData(None, None, False, True)
        
        
        # esp status data
        elif data_int == 0x8A8B8C8D8E8F9090:
            return ESP_StatusData(initialized=True)
        elif data_int == 0x8A8B8C8D8E8F9191:
            return ESP_StatusData(ready=True)
        elif data_int == 0x8A8B8C8D8E8F9292:
            return ESP_StatusData(image_sent=True)
        elif data_int == 0x8A8B8C8D8E8F9393:
            return ESP_StatusData(ready=False)
        
        else:
            return PictureData(data, None, False, False)
        