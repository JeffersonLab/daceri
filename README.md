# DACERI-local

Use the Logitech F310 Game Controller connected to the local RaspPi 4B and control the JLab DACERI robot with the [REV Control Hub](https://www.revrobotics.com/rev-31-1595/).

## External Modules
```bash
git submodule update --init  # Clone the submodules
```

- `hiddapi`: The underlying system-level support for python package `hid`. After `dnf/apt install hid`, if you still see the python import error such as cannot find certain *.so/*.dll files, you will need to compile and install the `hidapi` library by your self. Follow the docstrings in [detect_joystick.py](./scripts/detect_joystick.py) to see the process.

- `REVHubInterface`: The Python module for the REV Control Hub. By running `python -m REVHubInterface`, you should be able to see a GUI that can take the inputs from the GUI and control the Robot motors.

## Scripts
- [motor_test.py](./scripts/motor_test.py): Control one of the wheels (motors) with `REVHubInterface` without launching the GUI. If succeeded, the wheel will run for 3 seconds.
- [detect_joystick.py](./scripts/detect_joystick.py): Use the Python `hid` library to detect the Logitech F310 Game Controller, translate its inputs to a string and print the string to the screen.

### Notes
#### **Fix the `/dev/hidraw*` permission**

If you can print the gampad's vendor id and product id to the screen but it raises `HIDException` "Unable to open device" error, that is related to the permission for the device.

Check it with `ls -l /dev/hidraw*` (`hidraw1` in our case). If it’s owned by `root` or another group, the user can’t access it. Fix it by:

1. Create a udev rule: `sudo nano /etc/udev/rules.d/99-logitech-f310.rules`
2. In this rule file, add:
    ```
    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c216", MODE="0666"
    ```
   Replace the `idVendor` and `idProduct` with the HEX outputs of the Python file.
3. Reload the rule
    ```bash
    sudo udevadm control --reload
    sudo udevadm trigger
    ```

Rerun the Python script and the `HIDException` error should be gone.
