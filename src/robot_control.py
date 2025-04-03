"""
Control the robot via local Logitech Dual Action joystick input.
The REVHub is connected to the PI directly.
"""

import sys
import time

# Self-defined submoduels
import GamePad
from REVHubController import REVHubInputsTranslator

# Main function

gpad_device = GamePad.GamePadDevice()
translator = REVHubInputsTranslator()


# Get the REVHubModule
while True:
    report = gpad_device.get_gamepad_report()
    if report:
        translator.get_raw_state_from_report(report)
        translator.get_motor_control_input(True)
    else:
        print('\nUnable to get controller state')
        time.sleep(2)
