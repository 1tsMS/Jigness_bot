from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import mediapipe as mp
from collections import deque

class CVWorker(QThread):
    frame_ready = pyqtSignal(QImage)
    servo_data = pyqtSignal(int, int, int)

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self.running = False
        self.mutex = QMutex()  # Mutex for protecting shared data
        self.inner_ref = -90.0
        self.outer_ref = +90.0
        self._last_raw_wrist_signed = None

    def set_camera(self, cam_index):
        self.cam_index = cam_index

    def set_inner_calibration(self):
        self.mutex.lock()
        if self._last_raw_wrist_signed is not None:
            self.inner_ref = float(self._last_raw_wrist_signed)
        self.mutex.unlock()

    def set_outer_calibration(self):
        self.mutex.lock()
        if self._last_raw_wrist_signed is not None:
            self.outer_ref = float(self._last_raw_wrist_signed)
        self.mutex.unlock()

    def reset_calibration(self):
        self.mutex.lock()
        self.inner_ref = -90.0
        self.outer_ref = +90.0
        self.mutex.unlock()

    def run(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        mp_hands = mp.solutions.hands

        class Smoother:
            def __init__(self, window=7):
                self.buffers = [deque(maxlen=window) for _ in range(3)]
            def smooth(self, values):
                smoothed = []
                for i, val in enumerate(values):
                    self.buffers[i].append(val)
                    smoothed.append(float(np.mean(self.buffers[i])))
                return smoothed

        def angle_signed_deg(v1, v2):
            v1 = np.asarray(v1, dtype=np.float32)
            v2 = np.asarray(v2, dtype=np.float32)
            if np.linalg.norm(v1) < 1e-6 or np.linalg.norm(v2) < 1e-6:
                return 0.0
            v1 = v1 / np.linalg.norm(v1)
            v2 = v2 / np.linalg.norm(v2)
            dot = float(np.clip(np.dot(v1, v2), -1.0, 1.0))
            det = float(v1[0]*v2[1] - v1[1]*v2[0])
            return np.degrees(np.arctan2(det, dot))

        def calculate_angle(a, b, c):
            a, b, c = np.array(a), np.array(b), np.array(c)
            ba = a - b
            bc = c - b
            if np.linalg.norm(ba) < 1e-6 or np.linalg.norm(bc) < 1e-6:
                return 0.0
            cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))

        def map_wrist_to_servo(raw_signed_deg, inner_ref, outer_ref):
            if abs(outer_ref - inner_ref) < 1e-3:
                return 90.0
            t = (raw_signed_deg - inner_ref) / (outer_ref - inner_ref)
            return float(np.clip(t * 180.0, 0.0, 180.0))

        cap = cv2.VideoCapture(self.cam_index)
        smoother = Smoother(window=7)

        with mp_pose.Pose(min_detection_confidence=0.6,
                          min_tracking_confidence=0.6) as pose, \
             mp_hands.Hands(max_num_hands=1,
                            min_detection_confidence=0.6,
                            min_tracking_confidence=0.6) as hands:

            self.running = True
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                h, w, _ = frame.shape
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pose_results = pose.process(image_rgb)
                hand_results = hands.process(image_rgb)

                try:
                    lm = pose_results.pose_landmarks.landmark
                    shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                             lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    wrist_pose = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    hip = [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                           lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                    shoulder_px = (int(shoulder[0]*w), int(shoulder[1]*h))
                    elbow_px = (int(elbow[0]*w), int(elbow[1]*h))
                    wrist_px = (int(wrist_pose[0]*w), int(wrist_pose[1]*h))
                    hip_px = (int(hip[0]*w), int(hip[1]*h))

                    shoulder_angle = calculate_angle(hip, shoulder, elbow)
                    elbow_angle = calculate_angle(shoulder, elbow, wrist_pose)

                    wrist_servo = 90.0
                    raw_wrist_signed = 0.0

                    if hand_results.multi_hand_landmarks:
                        selected_hand = hand_results.multi_hand_landmarks[0]
                        if hand_results.multi_handedness:
                            for lms, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                                label = handedness.classification[0].label
                                if label == 'Right':
                                    selected_hand = lms
                                    break

                        hl = selected_hand.landmark
                        wrist_h = (int(hl[0].x * w), int(hl[0].y * h))
                        palm_center = (
                            int(((hl[5].x + hl[9].x + hl[13].x + hl[17].x) / 4) * w),
                            int(((hl[5].y + hl[9].y + hl[13].y + hl[17].y) / 4) * h)
                        )
                        v_forearm = np.array([wrist_px[0] - elbow_px[0], wrist_px[1] - elbow_px[1]], dtype=np.float32)
                        v_palm    = np.array([palm_center[0] - wrist_h[0], palm_center[1] - wrist_h[1]], dtype=np.float32)
                        raw_wrist_signed = angle_signed_deg(v_forearm, v_palm)

                        # Lock mutex to safely read calibration values
                        self.mutex.lock()
                        wrist_servo = map_wrist_to_servo(raw_wrist_signed, self.inner_ref, self.outer_ref)
                        local_inner = self.inner_ref
                        local_outer = self.outer_ref
                        self.mutex.unlock()

                        wrist_px = wrist_h

                    # Lock mutex to safely write the last raw angle
                    self.mutex.lock()
                    self._last_raw_wrist_signed = raw_wrist_signed
                    self.mutex.unlock()

                    shoulder_angle, elbow_angle, wrist_servo = smoother.smooth([
                        np.clip(shoulder_angle, 0, 180),
                        np.clip(elbow_angle, 0, 180),
                        np.clip(wrist_servo, 0, 180)
                    ])

                    # Draw pose skeleton
                    mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    cv2.putText(frame, f"{int(shoulder_angle)}", (shoulder_px[0] + 20, shoulder_px[1] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                    cv2.putText(frame, f"{int(elbow_angle)}", (elbow_px[0] + 20, elbow_px[1] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                    cv2.putText(frame, f"{int(wrist_servo)}", (wrist_px[0] - 40, wrist_px[1] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                    cv2.line(frame, hip_px, shoulder_px, (255,0,0), 3)
                    cv2.line(frame, shoulder_px, elbow_px, (255,0,0), 3)
                    cv2.line(frame, elbow_px, wrist_px, (255,0,0), 3)

                    # Use local copies for drawing to avoid holding the lock
                    hud = f"Calib inner: {local_inner:.1f}  outer: {local_outer:.1f}  raw_wrist: {raw_wrist_signed:.1f}"
                    cv2.putText(frame, hud, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,50,50), 2)

                    # Emit servo data
                    self.servo_data.emit(int(shoulder_angle), int(elbow_angle), int(wrist_servo))

                except AttributeError:
                    # This is expected when no pose is detected. Silently pass.
                    pass
                except Exception as e:
                    # Print any other unexpected errors to the console for debugging
                    print(f"Unexpected error in CVWorker: {e}")
                    pass

                # Convert frame for display
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                # Make a copy of the image data to prevent memory issues
                img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                self.frame_ready.emit(img)

                # Add a small delay to prevent overwhelming the system
                self.msleep(10) # ~10ms delay

            cap.release()

    def stop(self):
        self.running = False