import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer  # <-- Import QTimer
from Controller4 import Ui_MainWindow
import robot_functions as rf
from cv_worker import CVWorker

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- Rate-limit video updates to prevent UI crash ---
        self.latest_frame = None
        self.video_update_timer = QTimer(self)
        self.video_update_timer.setInterval(33)  # ~30 FPS
        self.video_update_timer.timeout.connect(self.render_latest_frame)
        self.video_update_timer.start()
        # ----------------------------------------------------

        # ===== Step sliders =====
        self.M1_step.valueChanged.connect(lambda v: rf.set_step(1, v))
        self.M2_step.valueChanged.connect(lambda v: rf.set_step(2, v))
        self.M3_step.valueChanged.connect(lambda v: rf.set_step(3, v))

        # ===== Base Rotation (continuous) =====
        self.BR_pos.pressed.connect(lambda: rf.adjust_br(100))  # forward
        self.BR_pos.released.connect(rf.stop_br)

        self.BR_neg.pressed.connect(lambda: rf.adjust_br(80))  # reverse
        self.BR_neg.released.connect(rf.stop_br)

        # ===== Positional Servos =====
        self.M1_pos.clicked.connect(lambda: rf.adjust_servo(1, +1))
        self.M1_neg.clicked.connect(lambda: rf.adjust_servo(1, -1))

        self.M2_pos.clicked.connect(lambda: rf.adjust_servo(2, +1))
        self.M2_neg.clicked.connect(lambda: rf.adjust_servo(2, -1))

        self.M3_pos.clicked.connect(lambda: rf.adjust_servo(3, +1))
        self.M3_neg.clicked.connect(lambda: rf.adjust_servo(3, -1))

        # ===== Stop only base rotation =====
        self.B_2.clicked.connect(rf.stop_br)
        self.RESET.clicked.connect(rf.reset_all)

        
        # ===== Cartesian Control =====
        self.Up.clicked.connect(lambda: rf.update_position(0, 1))
        self.Down.clicked.connect(lambda: rf.update_position(0, -1))
        self.Left.clicked.connect(lambda: rf.update_position(-1, 0))
        self.Right.clicked.connect(lambda: rf.update_position(1, 0))

        self.rot_pos.pressed.connect(lambda: rf.rotate_base(1))
        self.rot_neg.pressed.connect(lambda: rf.rotate_base(-1))
        self.rot_pos.released.connect(rf.stop_br)
        self.rot_neg.released.connect(rf.stop_br)

        # ===== Computer Vision =====
        self.cv_worker = None

        self.innerBtn.clicked.connect(self.set_inner_calib)
        self.outerBtn.clicked.connect(self.set_outer_calib)
        # Reset calibration (calls CVWorker.reset_calibration)
        if hasattr(self, "resetCalibBtn"):
            self.resetCalibBtn.clicked.connect(self.reset_calib)

        self.startBtn.clicked.connect(self.start_cv)
        self.stopBtn.clicked.connect(self.stop_cv)
        self.cam_select.currentIndexChanged.connect(self.change_camera)

        # view-only (preview framing/angles but DO NOT send to Arduino)
        self.viewBtn.clicked.connect(self.start_view)

        # ===== Arduino Connection =====
        self.connect_btn.clicked.connect(self.connect_arduino)

    def start_cv(self):
        if self.cv_worker:
            self.cv_worker.stop()
            self.cv_worker.wait()
        cam_index = self.cam_select.currentIndex()
        self.cv_worker = CVWorker(cam_index)
        self.cv_worker.frame_ready.connect(self.update_video)
        self.cv_worker.servo_data.connect(self.send_servo)   # sends to Arduino
        self.cv_worker.start()

    def start_view(self):
        """Start CV in preview mode: show frames and angles but do NOT send to Arduino."""
        if self.cv_worker:
            self.cv_worker.stop()
            self.cv_worker.wait()
        cam_index = self.cam_select.currentIndex()
        self.cv_worker = CVWorker(cam_index)
        self.cv_worker.frame_ready.connect(self.update_video)
        # intentionally do NOT connect servo_data -> send_servo
        self.cv_worker.start()

    def stop_cv(self):
        if self.cv_worker:
            self.cv_worker.stop()
            self.cv_worker.wait()
            self.cv_worker = None

    def change_camera(self, idx):
        if self.cv_worker:
            self.cv_worker.set_camera(idx)

    def update_video(self, img):
        """This slot just caches the latest frame from the worker thread."""
        self.latest_frame = img

    def render_latest_frame(self):
        """This slot is called by a timer to render the frame on the UI thread."""
        if self.latest_frame is not None:
            self.videoLabel.setPixmap(QPixmap.fromImage(self.latest_frame))

    def send_servo(self, s, e, w):
        # Invert the elbow angle because the motor is in the wrong direction
        inverted_elbow_angle = 180 - e
        rf.send_angles(s, inverted_elbow_angle, w) 

    def set_inner_calib(self):
        if self.cv_worker:
            self.cv_worker.set_inner_calibration()

    def set_outer_calib(self):
        if self.cv_worker:
            self.cv_worker.set_outer_calibration()

    def reset_calib(self):
        """Reset inner/outer wrist calibration to defaults in the CV worker."""
        if self.cv_worker:
            self.cv_worker.reset_calibration()

    def connect_arduino(self):
        port = "COM3"  # Or get from a QLineEdit/ComboBox if you want
        success = rf.connect_arduino(port)
        if not success:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Connection Error", f"Could not connect to Arduino on {port}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
