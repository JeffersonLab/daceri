"""
Test script for REV Expansion Hub.
The first motor should be run for 3 seconds at certain speed and then stop.
"""


import time

from REVHubInterface import REVcomm


TEST_MOTOR_NUM = 0

# Definitions in REVHubInterface.REVMotor.py
MOTOR_MODE_CONSTANT_POWER = 0
MOTOR_FLOAT_AT_ZERO = 1

# Main
try:
    commMod = REVcomm.REVcomm()
    commMod.openActivePort()
    REVModules = commMod.discovery()
    moduleNames = []
    for i in range(0, len(REVModules)):
        moduleNames.append('REV Expansion Hub ' + str(i))

    print(f"Totoal moduels: {len(REVModules)}")

    REVModules[0].motors[TEST_MOTOR_NUM].setMode(MOTOR_MODE_CONSTANT_POWER, MOTOR_FLOAT_AT_ZERO)
    REVModules[0].motors[TEST_MOTOR_NUM].enable()
    REVModules[0].motors[TEST_MOTOR_NUM].setPower(0.5*32000)
    time.sleep(3)
    REVModules[0].motors[TEST_MOTOR_NUM].disable()

except Exception as e:
    print(e)
    print("Error Searching for Hubs")
