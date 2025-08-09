#include <Servo.h>

Servo M[4];

void setup() {
  Serial.begin(9600);
  M[1].attach(10);  // Arm Base (position control)
  M[2].attach(11);  // Link 1
  M[3].attach(8);   // Link 2
  M[0].attach(12);  // Base 360 motor (slow rotation)
  M[0].write(90);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n'); // Read command line

    // Command format: M <id> <angle>
    // Example: "M 0 45" → Move servo 0 to 45°
    char cmd;
    int id, value;
    if (sscanf(input.c_str(), "%c %d %d", &cmd, &id, &value) == 3) {
      if (cmd == 'M' && id >= 0 && id < 4) {
        M[id].write(value);
        Serial.print("Moved servo ");
        Serial.print(id);
        Serial.print(" to ");
        Serial.println(value);
      }
    }
  }
}
