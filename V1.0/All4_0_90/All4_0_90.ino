#include <Servo.h>

Servo M[4];

void setup() {
  M[0].attach(10);  // Arm Base (position control)
  M[1].attach(11);  // Link 1
  M[2].attach(8);   // Link 2
  M[3].attach(12);  // Base 360 motor (slow rotation)
}

void loop() {
  // --- Start by stopping the base 360 motor ---
  M[3].write(90); // Neutral = stop

  // Sweep arm servos from 0 to 90
  for (int angle = 0; angle <= 90; angle += 2) {
    M[0].write(angle);
    M[1].write(angle);
    M[2].write(angle);
    delay(15);
  }

  delay(1000); // Hold

  // --- Slow rotate the base 360° motor forward for a short duration ---
  M[3].write(100); // Slightly forward
  delay(1500);     // Let it move slowly (tune as needed)
  M[3].write(90);  // Stop

  delay(1000); // Hold

  // Sweep back down
  for (int angle = 90; angle >= 0; angle -= 2) {
    M[0].write(angle);
    M[1].write(angle);
    M[2].write(angle);
    delay(15);
  }

  delay(1000); // Hold

  // Optional: Rotate base motor back slowly
  M[3].write(80); // Slightly reverse
  delay(1500);
  M[3].write(90); // Stop
}
