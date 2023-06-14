import websocket
import threading
import time

class WebSocketClient:

    def __init__(self, url = "ws://localhost:8080/", sender = None, log_level=1):
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(url,
                                         on_open = self.on_open,
                                         on_message = self.on_message,
                                         on_error = self.on_error,
                                         on_close = self.on_close)

        self.ws_thread = threading.Thread(target=self.start_receiving)
        self.is_stopped = False
        self.log_level = log_level
        self.sender = sender

    def start(self):
        self.ws_thread.start()

    def start_receiving(self):
        while True:
            if self.is_stopped:
                break
            try:
                self.ws.run_forever()
            except websocket.WebSocketException:
                if self.log_level > 1:
                    print("PC_websocket_server.py: Failed to connect, retrying in 5 seconds...")
                time.sleep(5)

    def on_message(self, ws, message):
        if self.log_level > 0:
            print(f"PC_websocket_server.py: Received message => {message}")
        self.send_data_to_esp32(message)

    def decode_web_command(self, data):
        if "forward" in data:
            return "MOVE:1"
        if "backward" in data:
            return "SEND_IMAGE"
        if "left" in data:
            return "ROTATE:-1"
        if "right" in data:
            return "ROTATE:-1"
        
        if self.log_level > 0:
            print("websocket client - ERROR: no matching command for " + data)
            return data


    def send_data_to_esp32(self, data):
        if self.sender is not None:
            self.sender.send(self.decode_web_command(data))

    def on_error(self, ws, error):
        if self.log_level > 0:
            print("PC_websocket_server.py: Error => ", end="")
            print(error)

    def on_close(self, ws, close_status_code, close_msg):
        if self.log_level > 0:
            print("PC_websocket_server.py: Connection closed")

    def on_open(self, ws):
        if self.log_level > 0:
            print("PC_websocket_server.py: Connection opened")
    
    def close(self):
        if self.log_level > 0:
            print("PC_websocket_server.py: closing websocket client...")
        self.is_stopped = True
        self.ws.close()
        self.ws_thread.join()
        if self.log_level > 0:
            print("PC_websocket_server.py: websocket client closed.")



if __name__ == "__main__":
    ws_client = WebSocketClient()
    ws_client.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    
    ws_client.close()
