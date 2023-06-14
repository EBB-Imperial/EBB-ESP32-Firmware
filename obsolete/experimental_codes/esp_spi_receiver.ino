#include <SPI.h>

const int slaveSelectPin = 5;
const int bufferSize = 64;
char receivedData[bufferSize];

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(slaveSelectPin, INPUT);
  SPI.setBitOrder(MSBFIRST);
}

void loop() {
  if (digitalRead(slaveSelectPin) == LOW) { // Check if data is available
    int index = 0;
    while (true) {
      char receivedChar = SPI.transfer(0x00);  // Receive data
      receivedData[index++] = receivedChar;
      if (receivedChar == '\0' || index >= bufferSize - 1) { // Check for end of message or buffer overflow
        receivedData[index] = '\0'; // Null-terminate the received string
        break;
      }
    }
    Serial.println("Received data: " + String(receivedData));
  }
}
