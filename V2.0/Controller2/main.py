import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Controller2 import Ui_MainWindow
import robot_functions as rf

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
