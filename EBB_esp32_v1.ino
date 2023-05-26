#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <AsyncWebSocket.h>


#define RXD2 16
#define TXD2 17

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
  }
}

void setup()
{
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
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

        ws.textAll(String(c));
    }
}
