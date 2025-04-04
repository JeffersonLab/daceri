"""
Control the robot via local Logitech Dual Action joystick input.
The REVHub is connected to the PI directly.
"""

import time


# Self-defined submoduels
import GamePad
from REVHubTranslator import REVHubInputsTranslator

# from REVHubInterface import REVcomm



class MyREVModule:
    """
    A class to interface with a REV module using the REV communication protocol.
    This class initializes a connection to the first discovered REV module
     through the REV communication interface. It handles the discovery of
     available modules and sets up the communication channel.

    Attributes:
        module: The first discovered REV module, or None if initialization fails.
    """
    def __init__(self):
        """
        Initializes the REV communication interface, discovers available
         REV modules, and sets the first discovered module as the active module.
        """
        self.module = None
        try:
            comm = REVcomm.REVcomm()
            comm.openActivePort()
            rev_modules = comm.discovery()

            print(f"Totoal modules: {len(rev_modules)}. Init the first one")
            self.module = rev_modules[0]

        except Exception as e:
            print(e)
            raise RuntimeError("REVHubINterface initialization failed.") from e


#------------------
#  Main function
#------------------
gpad_device = GamePad.GamePadDevice()
translator = REVHubInputsTranslator()

# Get the REVHubModule
# rev_module = MyREVModule()

while True:
    report = gpad_device.get_gamepad_report()
    if report:
        translator.get_raw_state_from_report(report)
        translator.get_motor_inputs(True)
        translator.get_servo_inputs(True)
    else:
        print('\nUnable to get controller state')
        time.sleep(1)
