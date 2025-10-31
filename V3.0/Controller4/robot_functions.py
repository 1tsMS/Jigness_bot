import serial
import math

arduino = None  # Do not connect on import

def connect_arduino(port="COM3", baudrate=9600):
    """Try to connect to Arduino. Returns True if successful, False otherwise."""
    global arduino
    try:
        arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        print(f"Connected to Arduino on {port}")
        return True
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        arduino = None
        return False

# ---------------- Arm Configuration ---------------- #
# Angles: [BR (360 servo), M1, M2, M3]
angles = [90, 0, 0, 0]  # BR starts at 90

# Step sizes for each motor (default)
steps = {1: 20, 2: 20, 3: 20}

# Link lengths in cm
L1 = 10.0
L2 = 7.0
L3 = 9.0

# Cartesian position of end effector
x = 20.0  # starting X
y = 0.0   # starting Y

# ---------------- Helper: Send Command ---------------- #
def send_servo(servo_id, angle):
    """Send angle command to specific servo."""
    global arduino
    if arduino is None or not arduino.is_open:
        print("Arduino not connected.")
        return
    angle = max(0, min(180, int(angle)))
    arduino.write(f"M {servo_id} {angle}\n".encode("utf-8"))
    print(f"Sent: M {servo_id} {angle}")

def send_angles(s, e, w):
    """Send shoulder, elbow, wrist angles (servos 1,2,3)."""
    send_servo(1, s)
    send_servo(2, e)
    send_servo(3, w)
    print(f"Sent angles: S={s}, E={e}, W={w}")

# ======================================================
#                    JOINT MODE
# ======================================================
def set_step(servo_id, value):
    """Set step size for joint control."""
    steps[servo_id] = value
    print(f"Step for M{servo_id} set to {value}")

def adjust_br(value):
    """Set continuous rotation servo speed directly."""
    angles[0] = max(0, min(180, value))
    send_servo(0, angles[0])

def adjust_servo(servo_id, direction):
    """Adjust positional servo by step size."""
    new_angle = angles[servo_id] + (steps[servo_id] * direction)
    new_angle = max(0, min(180, new_angle))
    angles[servo_id] = new_angle
    send_servo(servo_id, new_angle)

def stop_br():
    """Stop the base rotation motor."""
    angles[0] = 90
    send_servo(0, 90)
    print("Sent: M 0 90 (stop)")

# ======================================================
#                 CARTESIAN MODE (3-link IK)
# ======================================================
def inverse_kinematics_3link(target_x, target_y):
    """Compute joint angles for a 3-link planar arm."""
    dist = math.hypot(target_x, target_y)
    if dist > (L1 + L2 + L3):
        print("Target out of reach!")
        return None

    # Wrist position (joint 3 base)
    wrist_x = target_x - (L3 * target_x / dist)
    wrist_y = target_y - (L3 * target_y / dist)

    wrist_dist = math.hypot(wrist_x, wrist_y)

    # Joint 2 angle
    cos_angle2 = (wrist_dist**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_angle2 = max(-1, min(1, cos_angle2))  # clamp
    angle2 = math.acos(cos_angle2)

    # Joint 1 angle
    angle1 = math.atan2(wrist_y, wrist_x) - math.atan2(
        L2 * math.sin(angle2), L1 + L2 * math.cos(angle2)
    )

    # Joint 3 angle to keep end-effector aligned
    angle3 = math.atan2(target_y - wrist_y, target_x - wrist_x) - (angle1 + angle2)

    return math.degrees(angle1), math.degrees(angle2), math.degrees(angle3)

def update_position(dx, dy):
    """Move end effector in Cartesian space."""
    global x, y
    x += dx
    y += dy
    angles_deg = inverse_kinematics_3link(x, y)
    if angles_deg:
        angles[1] = angles_deg[0] + 90  # offset for mounting
        angles[2] = angles_deg[1]
        angles[3] = angles_deg[2] + 90
        send_servo(1, angles[1])
        send_servo(2, angles[2])
        send_servo(3, angles[3])

def rotate_base(direction):
    """Rotate base in Cartesian mode."""
    angles[0] += direction * 10
    angles[0] = max(0, min(180, angles[0]))
    send_servo(0, angles[0])

def reset_all():
    """Reset all motors to default positions."""
    global angles
    angles = [90, 0, 0, 0]
    send_servo(0, 90)  # base stop
    send_servo(1, 0)
    send_servo(2, 0)
    send_servo(3, 0)
    print("All motors reset to default.")
