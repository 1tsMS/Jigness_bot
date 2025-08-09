#include <Servo.h>

Servo M[4];

// Pins
const int potPin = A0;
const int joyX = A1;
const int joyY = A2;
const int buttonPin = A3;
const int vccPin = 0;

// Current positions
int pos0 = 90;  // M[0]
int pos1 = 60;  // M[1]
int stepSize = 1;

// Limits for M[1]
const int min1 = 0;
const int max1 = 120;

// Thresholds
const int deadZone = 50;

void setup() {
  M[0].attach(10);
  M[1].attach(11);
  M[2].attach(8);
  M[3].attach(12);

  pinMode(vccPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);  // Enable internal pull-up

  digitalWrite(vccPin, HIGH); // Power joystick

  M[0].write(pos0);
  M[1].write(pos1);
}

void loop() {
  // === Base 360° motor (M[3]) controlled by button ===
  int buttonVal = analogRead(buttonPin);
  if (buttonVal < 50) {
    M[3].write(100); // Clockwise
  } else {
    M[3].write(90);  // Stop
  }

  // === M[2] from potentiometer ===
  int potVal = analogRead(potPin);
  int angle2 = map(potVal, 0, 1023, 0, 180);
  M[2].write(angle2);

  // === M[0] and M[1] using joystick incrementally ===
  int xVal = analogRead(joyX);
  int yVal = analogRead(joyY);

  // Joystick X → M[0]
  if (xVal > 512 + deadZone && pos0 < 180) {
    pos0 += stepSize;
    M[0].write(pos0);
    delay(15);
  }
  else if (xVal < 512 - deadZone && pos0 > 0) {
    pos0 -= stepSize;
    M[0].write(pos0);
    delay(15);
  }

  // Joystick Y → M[1]
  if (yVal > 512 + deadZone && pos1 < max1) {
    pos1 += stepSize;
    M[1].write(pos1);
    delay(15);
  }
  else if (yVal < 512 - deadZone && pos1 > min1) {
    pos1 -= stepSize;
    M[1].write(pos1);
    delay(15);
  }

  // No delay at end — responsive control
}
