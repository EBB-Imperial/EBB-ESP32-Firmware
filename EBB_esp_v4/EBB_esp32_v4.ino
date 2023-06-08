#include "WiFi.h"
#include <vector>

// ------------------ TCP ------------------
#define TCP_PORT 1234
#define UDP_PACKET_SIZE 1027   // we send this much data in each packet

// ------------------ TCP Instructions ------------------
#define TCP_ABORT_HEADER 0x4747484849494A4A
#define TCP_IMAGE_FINISH 0x6767686869696A6A

// ------------------ UDP Headers ------------------
#define UDP_HEADER_SIZE 24          // three bytes for header
#define UDP_PACKET_PAYLOAD_SIZE (UDP_PACKET_SIZE - UDP_HEADER_SIZE)
// 1. Picture header
#define UDP_HEADER_PICTURE 0x000     // three bits for instruction
#define UDP_HEADER_PICTURE_INDEX 21  // 21 bits for picture index
// we will add other headers later

// ------------------ UART ------------------
#define UART_BAUD 1000000
#define URAT_BUFFER_SIZE 15104  // we cache this much data before dividing it into packets (151040 / 10) = 15104 bytes, i.e, 1/10 of picture
#define URAT_REQUEST_COUNT 10    // we will send this many requests to the FPGA per picture
#define URAT_TIMEOUT 1000       // we will wait this long for the FPGA to respond before sending another request

// ------------------ URAT Instructions ------------------
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

WiFiServer server(TCP_PORT);

uint8_t buffer[URAT_BUFFER_SIZE];
size_t request_count = 0;


std::vector<WiFiClient> clients;

// ------------------ Main ------------------


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

    server.begin();
    Serial.println("TCP Server started on IP: " + WiFi.softAPIP().toString() + ", Port: " + TCP_PORT);

    // send the first reset instruction
    Serial2.write(URAT_INSTRUCTION_RESET);
    state = FPGA_Comm_State::Resetting;
    Serial.println("FPGA_Comm_State: RESET");
}


void boardcast_message(uint8_t* message, size_t size)
{
    for (size_t i = 0; i < clients.size(); i++)
    {
        clients[i].write(message, size);
    }
}

void boardcast_message(uint64_t message)
{
    for (size_t i = 0; i < clients.size(); i++)
    {
        clients[i].write((uint8_t*)&message, 8);
    }
}


void loop()
{
    // check if there are any new clients
    WiFiClient client = server.available();
    if (client)
    {
        Serial.println("New client connected");
        clients.push_back(client);
    }

    // remove disconnected clients
    for (size_t i = 0; i < clients.size(); i++) {
        if (!clients[i].connected()) {
            Serial.println("Client disconnected");
            clients.erase(clients.begin() + i);
            i--;  // adjust index after removing element
        }
    }

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

            // send abort message to all clients
            boardcast_message(TCP_ABORT_HEADER);

            // reset the request count
            request_count = 0;

            state = FPGA_Comm_State::Requesting_Image;
            Serial.println("FPGA_Comm_State: REQUESTING_IMAGE");
            break;

        case FPGA_Comm_State::Requesting_Image: {
            // check if we've sent enough requests
            if (request_count >= URAT_REQUEST_COUNT - 1)
            {
                // send finish message to all clients
                boardcast_message(TCP_IMAGE_FINISH);

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
            // send the image to all clients
            boardcast_message(buffer, URAT_BUFFER_SIZE);
            request_count++;
            state = FPGA_Comm_State::Requesting_Image;
            break;
            
    }
}
