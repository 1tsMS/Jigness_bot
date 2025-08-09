#include <Servo.h>

Servo myServo;

void setup() {
  myServo.attach(9); // Connect servo signal to pin 9
}

void loop() {
  myServo.write(0);     // Move to 0 degrees
  delay(1000);          // Wait 1 second
  myServo.write(180);   // Move to 180 degrees
  delay(1000);          // Wait 1 second
}
