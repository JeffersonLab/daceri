"""
Control the robot via local Logitech Dual Action joystick input.
The REVHub is connected to the PI directly.
"""

import sys
import GamePad

# Main function
gamepad = GamePad.GamePadDevice()

if gamepad.get_gamepad_device() is None:
    print('Unable to find gamepad!')
    sys.exit(2)

# Get the REVHubModule
while True:
    report = gamepad.get_gamepad_report()
