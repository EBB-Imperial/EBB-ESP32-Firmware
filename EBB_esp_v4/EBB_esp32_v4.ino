#include "WiFi.h"
#include <vector>
#include <SoftwareSerial.h>
#include <string>

// ------------------ TCP ------------------
#define TCP_PORT 1234
#define UDP_PACKET_SIZE 1027   // we send this much data in each packet

// ------------------ TCP Instructions ------------------
// picture headers
#define TCP_START_HEADER 0x2727282829292A2A
#define TCP_ABORT_HEADER 0x4747484849494A4A
#define TCP_IMAGE_FINISH 0x6767686869696A6A

// instructions to pc headers
#define TCP_PC_INITIALIZED 0x8A8B8C8D8E8F9090
#define TCP_PC_READY 0x8A8B8C8D8E8F9191
#define TCP_PC_IMAGE_SENT 0x8A8B8C8D8E8F9292
#define TCP_PC_NOT_READY 0x8A8B8C8D8E8F9393

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
#define URAT_TIMEOUT 50       // we will wait this long for the FPGA to respond before sending another request

// ------------------ URAT Instructions ------------------
// 1. Reset to first byte of picture
#define URAT_INSTRUCTION_RESET 0x00
// 2. Request next 15104 bytes of picture
#define URAT_INSTRUCTION_REQUEST 0x01

// ------------------ Controller-ESP URAT Instructions ------------------
// instructions to send to the ESP
#define ESP_UART_INS_HCF 0x00   // TODO: change to query of accelerometer and gyroscope reading
#define ESP_UART_INS_STATUS 0x01
#define ESP_UART_INS_MOVE_STRAIGHT 0x02
#define ESP_UART_INS_TURN 0x03


// ------------------ Pins ------------------
#define RXD2 16
#define TXD2 17

// ------------------ Soft serial ------------------
#define RXD3 12
#define TXD3 14
#define SOFT_SERIAL_BAUD 115200

// ------------------------------------------

SoftwareSerial Serial3(RXD3, TXD3);

const char* ssid = "EBB_esp32_v1_AP";
const char* password = "EBBBBBBB";

WiFiServer server(TCP_PORT);

uint8_t buffer[URAT_BUFFER_SIZE];
size_t request_count = 0;

std::vector<WiFiClient> clients;

bool is_moving = false; // if true, we will not send images to clients

// message received from clients
String PC_message = "";
int decoded_result = 0;

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

    Serial3.begin(SOFT_SERIAL_BAUD);

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

    // send initialized and ready message to all clients
    boardcast_message(TCP_PC_INITIALIZED);
    boardcast_message(TCP_PC_READY);
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

void write_esp32_instruction(uint8_t instruction)
{
    Serial3.write(instruction);
}

void write_esp32_instruction(uint8_t* instruction, size_t size)
{
    Serial3.write(instruction, size);
}


int decode_PC_message(String message)
{
    // seperate the command into the command name and the command value
    int command_index = message.indexOf(':');
    String command_name = message;
    String command_value = "";
    if (command_index != -1)
    {
        command_name = message.substring(0, command_index);
        command_value = message.substring(command_index + 1);
    }

    // execute the command
    if (command_name == "MOVE")
    {
        // command for move is: 0x02 + distance value
        uint8_t instruction[2] = {ESP_UART_INS_MOVE_STRAIGHT, (uint8_t)command_value.toInt()};
        write_esp32_instruction(instruction, 2);
        Serial.println("Sended move instruction: " + String(instruction[0]) + ", " + String(instruction[1]));
    }
    else if (command_name == "ROTATE")
    {
        // command for rotate is: 0x03 + angle value
        uint8_t instruction[2] = {ESP_UART_INS_TURN, (uint8_t)command_value.toInt()};
        write_esp32_instruction(instruction, 2);
        Serial.println("Sended rotate instruction: " + String(instruction[0]) + ", " + String(instruction[1]));
    }
    else if (command_name == "HCF")
    {
        // command for HCF is: 0x00
        uint8_t instruction[1] = {ESP_UART_INS_HCF};
        write_esp32_instruction(instruction, 1);
        Serial.println("Sended HCF instruction: " + String(instruction[0]));
    }
    else if (command_name == "SEND_IMAGE")
    {
        return 1;   // 1 means ready to send image
    }
    else if (command_name == "SEND_SENSOR_DATA")
    {
        // TODO
    }
    else if (command_name == "QUERY_STATE")
    {
        switch (state)
        {
        case FPGA_Comm_State::Idle:
            boardcast_message(TCP_PC_READY);
            break;
        
        default:
            boardcast_message(TCP_PC_NOT_READY);
            break;
        }
    }
    else
    {
        Serial.println("ERROR: Unknown command received: " + command_name + " with value: " + command_value);
    }

    return 0;
}


void loop()
{
    // check if there are any new clients
    WiFiClient client = server.available();
    if (client)
    {
        Serial.println("New client connected");
        // kick out all previous clients
        for (size_t i = 0; i < clients.size(); i++) {
            clients[i].stop();
            clients.erase(clients.begin() + i);
            i--;  // adjust index after removing element
        }
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
            // pool data from esp32
            write_esp32_instruction(ESP_UART_INS_STATUS);
            if (Serial3.available() > 0)
            {
                uint8_t c = Serial3.read();
                if (c == 0x01)  // TODO: is this the right value?
                {
                    Serial.println("ESP32 is moving");
                    is_moving = true;
                }
                else
                {
                    is_moving = false;
                    // send ready message to all clients
                    boardcast_message(TCP_PC_READY);
                }
            }

            // read data from clients
            for (size_t i = 0; i < clients.size(); i++) {
                // check for incoming data
                //PC_message = "";
                while(clients[i].available() > 0) {
                    char c = clients[i].read();
                    if(c == '\n') {
                        Serial.println("Received message: " + PC_message);
                        decoded_result = decode_PC_message(PC_message);

                        switch(decoded_result)
                        {
                            case 1:
                                // send image to all clients
                                state = FPGA_Comm_State::Resetting;
                                Serial.println("FPGA_Comm_State: RESET");
                                break;
                        }
                        PC_message = "";
                    } else {
                        PC_message += c;
                    }
                }
            }
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
            if (request_count == 0)
            {
                // send start message to all clients
                boardcast_message(TCP_START_HEADER);
            }
            if (request_count >= URAT_REQUEST_COUNT)
            {
                // send finish message to all clients
                boardcast_message(TCP_IMAGE_FINISH);
                boardcast_message(TCP_PC_IMAGE_SENT);

                state = FPGA_Comm_State::Idle;
                Serial.println("FPGA_Comm_State: IDLE");
                break;
            }

            // check if we are moving, if so skip this loop
            if (is_moving)
            {
                Serial.println("ESP32 is moving, skipping request");
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