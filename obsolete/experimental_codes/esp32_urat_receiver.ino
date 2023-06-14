// This code is for ESP32 UART receiver

#define RXD2 16
#define TXD2 17

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
  Serial.println("ESP32 UART Receiver");
}

void loop() {
  while (Serial2.available()) {
    Serial.print((char)Serial2.read());
  }
}
