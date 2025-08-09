# 🛠️ Robot Arm Controller – PC & Arduino Serial Control

A **PyQt5-based desktop application** to control a robot arm via **serial communication** with an Arduino.  
Supports **individual motor jog control**, adjustable step sizes, and continuous base rotation control.

---

## 📸 Features
- **Graphical UI** built with **Qt Designer** & PyQt5.
- **Individual motor jog control**:
  - `M1`, `M2`, `M3` – positional servos.
  - `BR` – base rotation continuous servo.
- **Step size sliders** for M1, M2, M3.
- **Hold-to-move** support for BR motor.
- **Stop button** instantly resets BR motor to neutral (90°).
- **USB Serial Communication** with Arduino.
- Configurable step increments for precision or speed.

---

## 🖼️ UI Overview

| Mode           | Description |
|----------------|-------------|
| **Joint Mode** | Move each servo individually using + / – buttons. |
| **Cartesian Mode** | *(Planned)* Move the entire arm in X/Y/Z directions. |

---

## 🧩 Hardware Requirements
- Arduino Uno
- 3× Positional Servos (e.g., SG90, MG996R)
- 1× Continuous Rotation Servo for base
- USB cable to connect Arduino to PC

---

## 💻 Software Requirements
- Python **3.8+**
- [PyQt5](https://pypi.org/project/PyQt5/)
- [PySerial](https://pypi.org/project/pyserial/)

## 📂 Project Structure
