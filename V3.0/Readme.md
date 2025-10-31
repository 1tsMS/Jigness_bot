# Robotic Arm - Stage 3: Computer Vision Control (Hand Tracking)

This final stage adds **computer-vision-based control** to the robotic arm.  
The system tracks the user’s arm and wrist angles in real time using **MediaPipe Pose** and **Hands**, then maps those angles to servo movements via USB serial communication with Arduino.

---

## 🎯 Stage Goals
- ✅ Detect and track human arm joints (shoulder, elbow, wrist) using webcam input.  
- ✅ Map detected joint angles to the robotic arm’s servos.  
- ✅ Control the 4-DOF robot in real time through USB serial link.  
- ✅ Implement calibration for wrist rotation using reference gestures.  
- ✅ Integrate live video feed display inside the GUI for visual feedback.

---

## 🛠 Hardware
- **Robot:** 4-DOF robotic arm  
  - 1 × base rotation (MG995)  
  - 3 × link rotations (MG995)  
  - 1 × end-effector rotation (MG90S)
- **Controller:** Arduino Uno  
- **Camera:** USB or laptop webcam  
- **Power Supply:** 4 × 18650 Li-ion cells (external servo power)  
- **Laptop/PC:** runs Python CV + GUI

---

## 💻 Software
- **Python 3.x**
  - `mediapipe` – pose and hand landmark detection  
  - `opencv-python` – camera stream & display  
  - `numpy` – trigonometric angle computation  
  - `PyQt5` – GUI with live video panel  
  - `pyserial` – communication with Arduino
- **Arduino IDE** – servo-control firmware  
- **VS Code / Qt Designer** – development and UI design tools

---

## 🧠 How It Works
1. The camera feed is processed in a **background thread** (`CVWorker` class).  
2. MediaPipe extracts landmarks for the shoulder, elbow, wrist, hip, and hand.  
3. Computed joint angles are mapped to corresponding servo angles (0–180°).  
4. Smoothed and calibrated values are sent via serial to Arduino.  
5. The GUI overlays pose landmarks and provides manual calibration controls.

---

## ⚙️ Calibration
- **Inner / Outer wrist calibration** buttons allow setting personalized rotation limits.  
- Calibration offsets are stored during runtime for accurate mapping.  
- On-screen HUD displays calibration status and raw wrist readings.

---

## 📋 Results
- Stable real-time angle tracking and servo movement.  
- Smooth, natural robotic motion synchronized with human arm movement.  
- Robust calibration preventing erratic jumps.  
- Full integration between **computer vision**, **GUI**, and **Arduino hardware**.

---

## ⚠️ Known Issue
Currently, the program **stops responding after running for some time**.  
This appears to be related to **rapid frame loading** and **PyQt event-loop handling** within the threaded video-processing pipeline.  
The issue likely stems from excessive frame buildup or unhandled memory growth and needs further optimization in the CV thread.

---

## 🧩 Next Steps
- Improve frame-rate management and thread synchronization to fix GUI freeze.  
- Add left/right hand detection switching. 
- Redesign the bot with limits
---

## 📜 License
Open-source under the MIT License.
