import time
import math
import inputs
from REVHubInterface import REVcomm
from REVHubInterface import REVModule
from REVHubInterface import REVServo

# ----------------------------
# Gamepad State Reader
# ----------------------------
def get_gamepad_state(report):
    """
    Convert a report from the Logitech game controller to a state dictionary.
    """
    state = {}
    state['left_joy_H'] = max((float(report[0]) - 128.0) / 127.0, -1.0)
    state['left_joy_V'] = max((float(report[1]) - 128.0) / 127.0, -1.0)
    state['right_joy_H'] = max((float(report[2]) - 128.0) / 127.0, -1.0)
    state['right_joy_V'] = max((float(report[3]) - 128.0) / 127.0, -1.0)
    return state

# ----------------------------
# Setup Gamepad & Hub
# ----------------------------
gpad = inputs.devices.gamepads[0]
comm = REVcomm.REVComm()
hub = REVModule.REVHub(comm)

# Initialize motors
hub.setPortPairMode(0, "brake")
hub.setPortPairMode(1, "brake")
hub.setPortPairMode(2, "brake")

# ----------------------------
# Constants
# ----------------------------
DEADZONE = 0.05
CHANGE_THRESHOLD = 0.05
SIGNIFICANT_DROP = 0.1
MAX_THRESHOLD = 0.98

# Motor state
last_P1, last_P2, last_P3 = 0.0, 0.0, 0.0
was_max_P1, was_max_P2, was_max_P3 = False, False, False

# ----------------------------
# Motor Write Helper
# ----------------------------
def move_motor(index, value):
    value = max(min(value, 1.0), -1.0)  # Clamp
    hub.setMotor(index, value)

# ----------------------------
# Main Loop
# ----------------------------
print("Listening to gamepad...")
while True:
    report = gpad.read(512)
    if report:
        state = get_gamepad_state(report)
    else:
        time.sleep(0.005)
        continue

    if state:
        # Apply deadzone
        left_joy_V = state['left_joy_V'] if abs(state['left_joy_V']) > DEADZONE else 0.0
        left_joy_H = state['left_joy_H'] if abs(state['left_joy_H']) > DEADZONE else 0.0
        right_joy_H = state['right_joy_H'] if abs(state['right_joy_H']) > DEADZONE else 0.0

        # Calculate motor power
        P1 = -((2.0 / 3.0) * left_joy_H)
        P2 = -((-1.0 / 3.0) * left_joy_H + (1.0 / math.sqrt(3.0)) * left_joy_V)
        P3 = -((-1.0 / 3.0) * left_joy_H - (1.0 / math.sqrt(3.0)) * left_joy_V + (1.0 / 3.0) * right_joy_H)

        # --- Motor 1 ---
        if (abs(P1) < DEADZONE or
            abs(P1 - last_P1) > CHANGE_THRESHOLD or
            (was_max_P1 and abs(P1) < MAX_THRESHOLD - SIGNIFICANT_DROP)):

            move_motor(0, P1)
            was_max_P1 = abs(P1) >= MAX_THRESHOLD
            last_P1 = P1

        # --- Motor 2 ---
        if (abs(P2) < DEADZONE or
            abs(P2 - last_P2) > CHANGE_THRESHOLD or
            (was_max_P2 and abs(P2) < MAX_THRESHOLD - SIGNIFICANT_DROP)):

            move_motor(1, P2)
            was_max_P2 = abs(P2) >= MAX_THRESHOLD
            last_P2 = P2

        # --- Motor 3 ---
        if (abs(P3) < DEADZONE or
            abs(P3 - last_P3) > CHANGE_THRESHOLD or
            (was_max_P3 and abs(P3) < MAX_THRESHOLD - SIGNIFICANT_DROP)):

            move_motor(2, P3)
            was_max_P3 = abs(P3) >= MAX_THRESHOLD
            last_P3 = P3

    # Fast polling loop
    time.sleep(0.001)
