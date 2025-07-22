import inputs
import time
import os

# Motor ports
motor_ports = ["0", "1", "2"]
last_values = [0.0, 0.0, 0.0]  # optional, currently unused

def scale(x):
    # Deadband filter: ignore tiny joystick noise
    if abs(x) < 0.05:
        return 0.0
    else:
        return x

def move_motor(motor, power):
    # Convert to percent
    percent = int(power * 100)
    os.system(f"rev -m {motor} -p {percent}")

while True:
    try:
        # Read joystick events
        events = inputs.get_gamepad()

        # Initialize powers
        P1, P2, P3 = 0.0, 0.0, 0.0

        for event in events:
            if event.ev_type == "Absolute":
                # Read vertical axis on left stick
                if event.code == "ABS_Y":
                    P1 = scale(-event.state / 32768.0)  # reverse so forward is positive
                # Read vertical axis on right stick
                if event.code == "ABS_RY":
                    P2 = scale(-event.state / 32768.0)
                # D-Pad Up/Down for Motor 3
                if event.code == "ABS_HAT0Y":
                    if event.state == -1:
                        P3 = 1.0
                    elif event.state == 1:
                        P3 = -1.0
                    else:
                        P3 = 0.0

        # Always send current motor power (ensures instant stop/start)
        move_motor(0, P1)
        move_motor(1, P2)
        move_motor(2, P3)

        time.sleep(0.01)  # 100Hz update rate

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(0.1)
