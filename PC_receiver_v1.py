import websocket
import binascii

esp_ip_addr = "192.168.4.1"


# pretty printing
msg_row_index = 0
msg_col_index = 0
max_col_cnt = 10

def on_message(ws, message):
    global msg_col_index, msg_row_index
    msg_col_index += 1
    if (msg_col_index >= max_col_cnt):
        msg_row_index += 1
        msg_col_index = 0
        print("\n%d" % msg_row_index, end=" ")
    
    print(binascii.hexlify(message), end=" ")

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, reason=None, code=None):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection established")

#websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://" + esp_ip_addr + "/ws",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            subprotocols=["binary"])
ws.on_open = on_open

ws.run_forever()
