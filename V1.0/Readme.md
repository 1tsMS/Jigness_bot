# Robotic Arm - Stage 1: Servo Testing & Basic Control

This stage was aimed at verifying that all servos function correctly before building the full 4-DOF robotic arm.  
We tested motor movement through Arduino code and implemented simple control using a joystick module and potentiometer.

---

## 🔧 Stage Goals
- ✅ Test all servos for correct operation.
- ✅ Move each motor between 0° and 90° to verify range and torque.
- ✅ Control servos using:
  - Joystick module (X/Y axis control)
  - Potentiometer (angle control)

---

## 🛠 Hardware
- **Servos:**
  - 4 × MG995 (180° rotation)
  - 1 × MG90S (end-effector rotation)
- **Controller:** Arduino Uno
- **Control Inputs:**
  - 1 × Joystick module
  - 1 × Potentiometer
- **Power Supply:**
  - 4 × 18650 Li-ion cells (for servo load testing)
  - USB connection for Arduino

---

## 💻 Software
- **Arduino IDE**
- **Servo.h** library for PWM servo control

---

## 📋 Testing Results
- All MG995 and MG90S servos powered and rotated correctly.
- Joystick provided smooth analog control of servo angles.
- Potentiometer successfully set precise servo positions.

## 📜 License
Open-source under MIT License.
