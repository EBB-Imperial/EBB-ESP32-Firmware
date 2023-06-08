
class PictureData:
    def __init__(self, data, positionIndex, abort, finished) -> None:
        self.data = data
        self.positionIndex = positionIndex
        self.abort = abort
        self.finished = finished


class MessageDecoder:
    def __init__(self) -> None:
        pass

    def decode_package(self, data):
        data_int = int.from_bytes(data, byteorder='little')
        if data_int == 0x4747484849494A4A:
            print("received abort message: " + str(data_int))
            return PictureData(None, None, True, False)
        elif data_int == 0x6767686869696A6A:
            print("received finished message: " + str(data_int))
            return PictureData(None, None, False, True)
        else:
            return PictureData(data, None, False, False)
        