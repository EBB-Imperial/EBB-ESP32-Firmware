#include "WiFi.h"
#include "AsyncUDP.h"


// ------------------ UDP ------------------
#define UDP_PORT 1234
#define UDP_PACKET_SIZE 1024   // we send this much data in each packet


// ------------------ UART ------------------
#define UART_BAUD 1000000
#define URAT_BUFFER_SIZE 15104  // we cache this much data before dividing it into packets (151040 / 10) = 15104 bytes, i.e, 1/10 of picture
#define URAT_REQUEST_COUNT 10    // we will send this many requests to the FPGA per picture
#define URAT_TIMEOUT 1000       // we will wait this long for the FPGA to respond before sending another request

// instructions for FPGA
// 1. Reset to first byte of picture
#define URAT_INSTRUCTION_RESET 0x00
// 2. Request next 15104 bytes of picture
#define URAT_INSTRUCTION_REQUEST 0x01


// ------------------ Pins ------------------
#define RXD2 16
#define TXD2 17

// ------------------------------------------


const char* ssid = "EBB_esp32_v1_AP";
const char* password = "EBBBBBBB";

AsyncUDP udp;
uint8_t buffer[URAT_BUFFER_SIZE];
size_t request_count = 0;

// a state machine to keep track of what we're doing
enum class FPGA_Comm_State
{
    Idle,
    Resetting,
    Requesting_Image,
    Sending_Image,
};

FPGA_Comm_State state = FPGA_Comm_State::Idle;

void setup()
{
    Serial.begin(UART_BAUD);
    Serial2.begin(UART_BAUD, SERIAL_8N1, RXD2, TXD2);
    Serial2.setTimeout(URAT_TIMEOUT);
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

    // send the first reset instruction
    Serial2.write(URAT_INSTRUCTION_RESET);
    state = FPGA_Comm_State::Resetting;
    Serial.println("FPGA_Comm_State: RESET");
}

void loop()
{
    // state machine
    switch (state)
    {
        case FPGA_Comm_State::Idle:
            // move to the Resetting state
            state = FPGA_Comm_State::Resetting;
            break;

        case FPGA_Comm_State::Resetting:
            // send a reset command and move to the Requesting_Image state
            Serial2.write(URAT_INSTRUCTION_RESET);

            // reset the request count
            request_count = 0;

            state = FPGA_Comm_State::Requesting_Image;
            Serial.println("FPGA_Comm_State: REQUESTING_IMAGE");
            break;

        case FPGA_Comm_State::Requesting_Image: {
            // check if we've sent enough requests
            if (request_count >= URAT_REQUEST_COUNT)
            {
                state = FPGA_Comm_State::Idle;
                Serial.println("FPGA_Comm_State: IDLE");
                break;
            }

            // instruction for requesting image: request instruction + number of bytes to request
            uint8_t request_instruction[3] = {URAT_INSTRUCTION_REQUEST, URAT_BUFFER_SIZE & 0xff, (URAT_BUFFER_SIZE >> 8) & 0xff};
            Serial2.write(request_instruction, 3);
            
            // reading bytes from URAT will block until we get URAT_BUFFER_SIZE bytes or until URAT_TIMEOUT
            size_t bytes_read = Serial2.readBytes(buffer, URAT_BUFFER_SIZE);

            if (bytes_read == URAT_BUFFER_SIZE)
            {
                state = FPGA_Comm_State::Sending_Image;
                Serial.println("FPGA_Comm_State: SENDING_IMAGE");
            }
            else
            {
                state = FPGA_Comm_State::Resetting;
                Serial.println("*** ERROR: FPGA response was the wrong size. Expected " + String(URAT_BUFFER_SIZE) + " bytes, but got " + String(bytes_read) + " bytes. ***");
                Serial.println("FPGA_Comm_State: RESET");
            }

            break;
        }

        case FPGA_Comm_State::Sending_Image:
            // split the buffer into UDP_PACKET_SIZE chunks and send them
            // if we've sent all the chunks, move to the Requesting_Image state
            for (int i = 0; i < URAT_BUFFER_SIZE; i += UDP_PACKET_SIZE)
            {
                udp.broadcastTo(buffer + i, UDP_PACKET_SIZE, UDP_PORT);
            }
            request_count++;
            state = FPGA_Comm_State::Requesting_Image;
            break;
            
    }
}
