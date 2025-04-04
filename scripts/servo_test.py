"""
Test script for REV Expansion Hub.

Get the period and pulse width of the first servo.
"""


import time

from REVHubInterface import REVcomm


TEST_SERVO_ID = 0

# Main
commMod = REVcomm.REVcomm()
commMod.openActivePort()
REVModules = commMod.discovery()

module = REVModules[0]

try:
    period = module.servos[TEST_SERVO_ID].getPeriod()
    pulse_width = module.servos[TEST_SERVO_ID].getPulseWidth()
    print(f"Servo {TEST_SERVO_ID}: period={period}, pulse_width={pulse_width}")

except (AttributeError, IndexError, RuntimeError) as e:  # Replace with specific exceptions
    print(e)
    print("Error getting servo information")
