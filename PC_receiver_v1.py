import websocket

esp_ip_addr = "192.168.4.1"

def on_message(ws, message):
    try:
        print("Received message:", message)
    except Exception as e:
        print("Error in on_message:", str(e))

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, *args):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection established")

websocket.enableTrace(True)

try:
    ws = websocket.WebSocketApp("ws://" + esp_ip_addr + "/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    ws.run_forever()
except Exception as e:
    print("An exception occurred:", str(e))
