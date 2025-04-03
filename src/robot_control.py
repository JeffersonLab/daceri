"""
Control the robot via local Logitech Dual Action joystick input.
The REVHub is connected to the PI directly.
"""

import sys
import time

# Self-defined submoduels
import GamePad

# Main function
gpad_device = GamePad.GamePadDevice()

if gpad_device.gamepad is None:
    print('Unable to find gamepad!')
    sys.exit(2)

# Get the REVHubModule
while True:
    report = gpad_device.get_gamepad_report()
    if report != b'':
        print(report)
    time.sleep(1)
