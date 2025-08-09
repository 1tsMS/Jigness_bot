import serial

# Connect to Arduino
arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)

# Angles: [BR (360 servo), M1, M2, M3]
angles = [90, 0, 0, 0]  # BR starts at 90

# Step sizes for each motor (default)
steps = {1: 20, 2: 20, 3: 20}

def set_step(servo_id, value):
    """Set the step size for a motor."""
    steps[servo_id] = value
    print(f"Step for M{servo_id} set to {value}")

def adjust_br(value):
    """Set continuous rotation servo speed directly."""
    angles[0] = max(0, min(180, value))
    command = f"M 0 {angles[0]}\n"
    arduino.write(command.encode("utf-8"))
    print(f"Sent: {command.strip()}")

def adjust_servo(servo_id, direction):
    """Adjust positional servo by step size."""
    new_angle = angles[servo_id] + (steps[servo_id] * direction)
    new_angle = max(0, min(180, new_angle))
    angles[servo_id] = new_angle
    command = f"M {servo_id} {new_angle}\n"
    arduino.write(command.encode("utf-8"))
    print(f"Sent: {command.strip()}")

def stop_br():
    """Stop the base rotation motor."""
    angles[0] = 90
    arduino.write(f"M 0 90\n".encode("utf-8"))
    print("Sent: M 0 90 (stop)")
