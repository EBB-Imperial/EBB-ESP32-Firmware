#include <SPI.h>

const int slaveSelectPin = 5;
const char* message = "Hello, ESP32 Board 2!";

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(slaveSelectPin, OUTPUT);
}

void loop() {
  digitalWrite(slaveSelectPin, LOW);  // Start SPI transmission

  for (int i = 0; i < strlen(message); i++) {
    SPI.transfer(message[i]);  // Send each character
  }

  digitalWrite(slaveSelectPin, HIGH); // End SPI transmission

  delay(1000);  // Wait for a second
}
