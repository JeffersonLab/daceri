import inputs
import os
import time

# Track current power per motor (joystick value)
last_P1 = 0
last_P2 = 0
last_P3 = 0

# Motor control (replace with actual motor command if needed)
def move_motor(motor, power):
    percent = int(power * 100)
    print(f"Motor {motor} -> Power {percent}%")
    # Example of real motor command (uncomment and edit this line):
    # os.system(f"motorctl -m {motor} -p {percent}")

# Map axis codes from Logitech F310
AXIS_MAP = {
    'ABS_Y': 0,   # Left joystick vertical
    'ABS_RZ': 1,  # Right trigger
    'ABS_Z': 2,   # Left trigger
}

def normalize(value):
    # Normalize analog value from [-32768, 32767] or [0, 255] to [-1.0, 1.0]
    if value >= -32768 and value <= 32767:
        return round(value / 32767, 2)
    elif value >= 0 and value <= 255:
        return round((value - 128) / 127, 2)
    else:
        return 0.0

print("Controller initialized. Move joystick or triggers...")

while True:
    events = inputs.get_gamepad()
    for event in events:
        if event.ev_type == 'Absolute':
            value = normalize(event.state)

            if event.code == 'ABS_Y':  # Motor 0
                if value != last_P1:
                    last_P1 = value
                    move_motor(0, value)

            elif event.code == 'ABS_RZ':  # Motor 1
                if value != last_P2:
                    last_P2 = value
                    move_motor(1, value)

            elif event.code == 'ABS_Z':  # Motor 2
                if value != last_P3:
                    last_P3 = value
                    move_motor(2, value)
