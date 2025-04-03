"""
The GamePad Module to find the device and get its report.
"""

import hid

GAMEPAD_PRODUCT_STR = 'Logitech Dual Action'


class GamePadDevice:
    """
    A class to interface with a Logitech Dual Action game controller.

    This class provides methods to detect and connect to the game controller
     and retrieve raw input reports from it.

    Attributes:
        gamepad (hid.Device): The HID device object representing the game controller.

    Methods:
        get_gamepad_report():
            Retrieves the raw input report from the connected game controller.
    """

    def __init__(self, product_str=GAMEPAD_PRODUCT_STR):
        self.gamepad = None

        for d in hid.enumerate():
            if d['product_string'] == product_str:
                vendor_id  = int(d['vendor_id' ])
                product_id = int(d['product_id'])
                path = d['path']
                print(f"Found Logitech gamepad: vendor_id: [0x{vendor_id:x}], product_id: [0x{product_id:x}]")
                print(f"Device path: {str(path)}\n")
                # NOTE: Check the path permission if there is HID "Unable to open device" error
                self.gamepad = hid.Device(path=path)
                self.gamepad.nonblocking = True

        if self.gamepad is None:
            print("Unable to find gamepad!")
            raise RuntimeError("GamePadDevice initialization failed.")

        print("GamePadDevice initialized.")
        print("Print 'L3' to enable all motors.")
        print("Print 'R3' to enable all servos.")

    def get_gamepad_report(self):
        """Get the raw report from the gamepad device."""
        return self.gamepad.read(512)
