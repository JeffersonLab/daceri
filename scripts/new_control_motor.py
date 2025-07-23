import math
import time
import sys
import hid
from REVHubInterface import REVcomm
from REVHubInterface import REVModule
from REVHubInterface import REVServo

#-------------------------------------
# LogitechReportToState
#-------------------------------------
def get_gamepad_state(report):
    state = {}
    state['left_joy_H'] = max((float(report[0])-128.0)/127.0, -1.0)
    state['left_joy_V'] = max((float(report[1])-128.0)/127.0, -1.0)
    state['right_joy_H'] = max((float(report[2])-128.0)/127.0, -1.0)
    state['right_joy_V'] = max((float(report[3])-128.0)/127.0, -1.0)
    dpad = report[4] & 0b00001111
    state['dpad_up'] = (dpad == 0) or (dpad == 1) or (dpad == 7)
    state['dpad_down'] = (dpad == 3) or (dpad == 4) or (dpad == 5)
    state['dpad_left'] = (dpad == 5) or (dpad == 6) or (dpad == 7)
    state['dpad_right'] = (dpad == 1) or (dpad == 2) or (dpad == 3)
    state['button_X'] = (report[4] & 0b00010000) != 0
    state['button_A'] = (report[4] & 0b00100000) != 0
    state['button_B'] = (report[4] & 0b01000000) != 0
    state['button_Y'] = (report[4] & 0b10000000) != 0
    state['bumper_left'] = (report[5] & 0b00000001) != 0
    state['bumper_right'] = (report[5] & 0b00000010) != 0
    state['trigger_left'] = (report[5] & 0b00000100) != 0
    state['trigger_right'] = (report[5] & 0b00001000) != 0
    state['back'] = (report[5] & 0b00010000) != 0
    state['start'] = (report[5] & 0b00100000) != 0
    state['L3'] = (report[5] & 0b01000000) != 0
    state['R3'] = (report[5] & 0b10000000) != 0
    return state

#-------------------------------------
# Setup HID (game controller)
#-------------------------------------
def get_gamepad():
    gamepad = None
    for d in hid.enumerate():
        if d['product_string'] == 'Logitech Dual Action':
            vendor_id = int(d['vendor_id'])
            product_id = int(d['product_id'])
            path = d['path']
            print(f'Found Logictech gamepad: vendor_id: [0x{vendor_id:x}], product_id:[0x{product_id:x}]')
            gamepad = hid.Device(path=path)
            gamepad.nonblocking = True
    return gamepad

def set_gamepad_enable_all(val):
    for i in range(4):
        print(f"enable M{i} {val}")
    for i in range(8):
        print(f"enable S{i} {val}")

def move_motor(motor_id, speed, last_speeds):
    speed = max(min(speed, 1.0), -1.0)  # Clamp
    if abs(speed - last_speeds[motor_id]) > 0.03:
        REVModules[0].motors[motor_id].setPower(int(speed * 32000))
        last_speeds[motor_id] = speed

#-------------------------------------
# Initialize REV Hub and Motors
#-------------------------------------
commMod = REVcomm.REVcomm()
commMod.openActivePort()
REVModules = commMod.discovery()
moduleNames = [f'REV Expansion Hub {i}' for i in range(len(REVModules))]
print(f"Total Modules: {len(moduleNames)}")

for motor_num in range(4):
    REVModules[0].motors[motor_num].enable()
    REVModules[0].motors[motor_num].setMode(0, 1)
    print(f"Motor {motor_num} initialized")

# Optional: initialize servo pulse
for servos in range(2):
    REVModules[0].servos[servos].setPulseWidth(1000)

#-------------------------------------
# Main Loop
#-------------------------------------
gpad = get_gamepad()
if gpad is None:
    print('Unable to find gamepad!')
    sys.exit(2)
else:
    last_speeds = [0.0 for _ in range(4)]

    while True:
        report = gpad.read(512)
        if report:
            state = get_gamepad_state(report)
        else:
            continue  # Skip iteration if no data

        # Deadband filtering
        left_joy_V = state['left_joy_V'] if abs(state['left_joy_V']) > 0.05 else 0
        left_joy_H = state['left_joy_H'] if abs(state['left_joy_H']) > 0.05 else 0
        right_joy_V = state['right_joy_V'] if abs(state['right_joy_V']) > 0.05 else 0
        right_joy_H = state['right_joy_H'] if abs(state['right_joy_H']) > 0.05 else 0

        # Kinematic translation
        P1 = (2.0/3.0)*left_joy_H
        P2 = (-1.0/3.0)*left_joy_H + (1.0/math.sqrt(3.0))*left_joy_V
        P3 = (-1.0/3.0)*left_joy_H - (1.0/math.sqrt(3.0))*left_joy_V + (1.0/3.0)*right_joy_H

        # Reverse direction
        P1, P2, P3 = -P1, -P2, -P3

        # Filter small values
        P1 = 0 if abs(P1) < 0.05 else P1
        P2 = 0 if abs(P2) < 0.05 else P2
        P3 = 0 if abs(P3) < 0.05 else P3

        # Send motor commands only if changed
        move_motor(0, P1, last_speeds)
        move_motor(1, P2, last_speeds)
        move_motor(2, P3, last_speeds)

        # Optional sleep to smooth updates
        time.sleep(0.005)
