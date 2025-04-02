import hid

PRODUCT_STR = 'Logitech Dual Action'


class GamePadDevice:
    """
    A class to interface with a Logitech Dual Action game controller.

    This class provides methods to detect and connect to the game controller
     and retrieve raw input reports from it.

    Attributes:
        gamepad (hid.Device): The HID device object representing the game controller.
        gamepad_report (list): The raw input report data from the game controller.

    Methods:
        get_gamepad_device():
            Searches for the Logitech Dual Action game controller and initializes
             the `gamepad` attribute with the corresponding HID device.

        get_gamepad_report():
            Retrieves the raw input report from the connected game controller.
    """

    def __init__(self):
        self.gamepad = None

    def get_gamepad_device(self):
        """
        Find the Logitech game controller and return the device object."
        """
        for d in hid.enumerate():
            if d['product_string'] == PRODUCT_STR:
                # print(f"vid={d['vendor_id' ]}, pid={d['product_id']}, path={d['path']}")
                vendor_id  = int(d['vendor_id' ])
                product_id = int(d['product_id'])
                path = d['path']
                print('Found Logictech gamepad: vendor_id: [0x%x], product_id:[0x%x]'%(vendor_id, product_id))
                print(f"\tDevice path: {path}")
                # NOTE: Check the path permission if there is HID "Unable to open device" error
                self.gamepad = hid.Device(path=path)
                self.gamepad.nonblocking = True

    def get_gamepad_report(self):
        """Get the raw report from the gamepad device."""
        return self.gamepad.read(512)
