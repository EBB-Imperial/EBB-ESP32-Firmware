#include "WiFi.h"
#include "AsyncUDP.h"

#define RXD2 16
#define TXD2 17

#define UART_BAUD 1000000
#define UDP_PORT 1234
#define BUFFER_SIZE 150400  // adjust this value based on your requirements

const char* ssid = "EBB_esp32_v1_AP";
const char* password = "EBBBBBBB";

AsyncUDP udp;
uint8_t buffer[BUFFER_SIZE];
size_t buffer_index = 0;

void setup()
{
    Serial.begin(UART_BAUD);
    Serial2.begin(UART_BAUD, SERIAL_8N1, RXD2, TXD2);
    Serial.println("UART Initialized");

    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);

    if (udp.listen(UDP_PORT)) {
        Serial.println("UDP Listening on IP: " + WiFi.softAPIP().toString() + ", Port: " + UDP_PORT);

        udp.onPacket([](AsyncUDPPacket packet) {
            Serial.println("Received a UDP packet");
        });
    } else {
        Serial.println("Failed to bind UDP");
    }
}

void loop()
{
    // while (Serial2.available() && buffer_index < BUFFER_SIZE)
    // {
    //     char c = Serial2.read();
    //     buffer[buffer_index++] = c;

    //     if (buffer_index == BUFFER_SIZE)
    //     {
    //         udp.broadcastTo(buffer, buffer_index, UDP_PORT);
    //         buffer_index = 0;
    //     }
    // }

    // If there's no more data to read and the buffer isn't empty, send the remaining bytes.
    // if (!Serial2.available() && buffer_index > 0)
    // {
    //     udp.broadcastTo(buffer, buffer_index, UDP_PORT);
    //     buffer_index = 0;
    // }

    // here, we want to test the maximum memory size ESP32 can handle
    // we will simply fill the buffer with 0xFF, and everytime when buffer is full, we log a message in the serial monitor
    while (buffer_index < BUFFER_SIZE)
    {
        buffer[buffer_index++] = 0xFF;
    }

    buffer_index = 0;

    Serial.println("Buffer is full");
}
