# header format: three bytes for header. First three bits are for package type
# 0b100: image data
# 0b101: sensor data (TODO)
# 0b010: new picture chunk

class PictureData:
    def __init__(self, data, positionIndex, new_chunk) -> None:
        self.data = data
        self.positionIndex = positionIndex
        self.new_chunk = new_chunk


class MessageDecoder:
    def __init__(self) -> None:
        self.new_chunk = False

    def get_package_header(self, data):
        return data[0] >> 5
    
    def decode_package(self, data):
        # header format: three bytes for header. First three bits are for package type
        # 0b100: image data
        # 0b101: sensor data (TODO)
        # 0b010: new picture chunk
        
        # print the first three bytes in binary format, i.e, data[:3]
        #print("receiver.py: received data: ", bin(data[0]), bin(data[1]), bin(data[2]))
     
        package_format = self.get_package_header(data)

        if package_format == 0b100:
            # image data
            # get the position index: the last 5 bits of the first byte plus the second and third byte
            positionIndex = (data[0] & 0b00011111) << 16 | data[1] << 8 | data[2]
            # get the image data
            imageData = data[3:]
            #print("receiver.py: received image data, position index: ", positionIndex)
            new_chunk = self.new_chunk
            self.new_chunk = False

            return PictureData(imageData, positionIndex, new_chunk)
        
        if package_format == 0b010:
            # new picture chunk
            # mark the new chunk flag
            self.new_chunk = True
            print("decoder.py: received new picture chunk")