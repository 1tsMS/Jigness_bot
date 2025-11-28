# Jigness_bot
# 4-DOF Arduino Robotic Arm

A 4-DOF robotic arm with base rotation, 3 link rotations, and end-effector rotation using an MG90S servo.  
Controlled via Arduino Uno over USB serial connection from a Python GUI.

## 🔧 Features
- **4 DOF movement:**
  - 1 × Base rotation (MG995)
  - 3 × Link rotations (MG995)
  - End-effector rotation via MG90S
- **USB Serial Control** from laptop
- **Safe angle limits** to prevent collisions
- **Custom-designed in Fusion 360**
- Runs entirely on Arduino Uno + Python GUI

---

## 🛠 Hardware
- **Servos:**
  - 4 × MG995 (180° rotation)
  - 1 × MG90S (end-effector rotation)
- **Controller:** Arduino Uno
- **Power Supply:** 4 × 18650 Li-ion cells (in series/parallel configuration)
- **Laptop/PC** for GUI control

---

## 💻 Software
- **Arduino IDE** (servo control firmware)
- **Python 3.x**
- **VS Code** (development environment)
- **PySerial** (USB communication)
- **PyQt5** (GUI framework)
- **Qt Designer** (UI design)
- **Fusion 360** (mechanical design)

