# DACERI-local

Use the Logitech F310 Game Controller connected to the local RaspPi 4B and control the JLab DACERI robot with the [REV Control Hub](https://www.revrobotics.com/rev-31-1595/).

## External Modules
```bash
git submodule update --init  # Clone the submodules
```

- `hiddapi`: The underlying system-level support for python package `hid`. After `dnf/apt install hid`, if you still see the python import error such as cannot find certain *.so/*.dll files, you will need to compile and install the `hidapi` library by your self. Follow the docstrings in [detect_joystick.py](./scripts/detect_joystick.py) to see the process.

- `REVHubInterface`: The Python module for the REV Control Hub. By running `python -m REVHubInterface`, you should be able to see a GUI that can take the inputs from the GUI and control the Robot motors.

## Scripts
- [detect_joystick.py](./scripts/detect_joystick.py) Use the Python `hid` library to detect the Logitech F310 Game Controller,  translate its inputs to a string and print the string to the screen.
