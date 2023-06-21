#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <AsyncWebSocket.h>


#define RXD2 16
#define TXD2 17

#define UART_BAUD 1000000

const char* ssid = "EBB_esp32_v1_AP";
const char* password = "EBBBBBBB";

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len)
{
  if (type == WS_EVT_CONNECT) {
    Serial.println("WebSocket client connected");
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.println("WebSocket client disconnected");
  } else if (type == WS_EVT_DATA) {
    // If any data is received, write it out to the serial
    for(size_t i=0; i<len; i++) {
      Serial2.write(data[i]);
    }
  }
}

void setup()
{
  Serial.begin(UART_BAUD);
  Serial2.begin(UART_BAUD, SERIAL_8N1, RXD2, TXD2);
  Serial.println("UART Initialized");
  
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.addHandler(&ws);
  ws.onEvent(onWebSocketEvent);

  server.begin();
}

void loop()
{
    while (Serial2.available()) 
    {
        char c = Serial2.read();
        Serial.print(c);
        if (c == '\n')
        {
            Serial.println();
        }

        // create a uint8_t array with a single element
        uint8_t binaryData[1] = {(uint8_t)c};

        // send the binary data to all connected clients
        ws.binaryAll(binaryData, sizeof(binaryData));
    }
}