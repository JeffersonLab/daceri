# robot-project
Any and all code for the DACERI (DAta CEnter Robot Inspector) project in affiliation with Jefferson Lab.

## Example Video
[Demonstration of the Robot](https://www.youtube.com/watch?v=JDuZJEAZcf4&t=47s)

## Links
- [Parts List](https://docs.google.com/spreadsheets/d/1oFqTVsd3Hdgb1OTtmRurlVj-2fMQM05GRbAsK3FwgG0/edit?usp=sharing)
- [Thesis](https://drive.google.com/file/d/1kZYvtbdwQk6LjgCDchcMXePofmcdOxIe/view?usp=sharing)

## Run Simulation
1. Download the respective file based on OS and architecture: [https://github.com/google-deepmind/mujoco/releases](https://github.com/google-deepmind/mujoco/releases/latest)
2. Extract the file, and run **simulate** inside the extracted folder. Mujoco simulator should run
3. Clone this repository
4. Go into the **sim/** directory
5. Drag-and-drop any .xml into the simulator

## Edit/Print 3D model parts
1. Clone this repository
2. Go into the **designs/** directory
3. Choose any design you'd like
4. Open in any CAD software, make changes, and export as STL
5. Use a program like [UltiMaker Cura](https://ultimaker.com/software/ultimaker-cura/) or [Prusa Slicer](https://github.com/prusa3d/PrusaSlicer/releases) and slice the STL file into GCODE
6. Run the GCODE file on a 3D printer

## Move the robot
1. Clone this repository on both the client computer and the robot's R-Pi
2. On the robot's R-Pi, run the following steps according to your desired setup:
   * Run this first:
     ```
     python -m venv ./.venv --system-site-packages
     pip install -r /path/to/daceri/libs/requirements.txt
     source ./.venv/bin/activate
     ```
   * UDP Server (Modify the IP Address in the udp-server.py file to the IP of the R-Pi):
     ```
     python /path/to/daceri/scripts/udp-server.py
     ```
   * Websockets Server:
     ```
     python /path/to/daceri/scripts/websockets.py
     ```
4. Go into the **scripts/** directory
5. Use the provided Dockerfile ([Wiki: How to download and install Docker](https://docs.docker.com/get-started/get-docker/)) to automatically setup the correct packages and libraries or use a Linux/MacOS system with Python installed
   * Container:
     ```
     cd ./robot-project
     docker build -t robot-container .
     docker run -v `pwd`:/work/robot:Z -v /dev/input:/dev/input:ro --rm -it robot-container:latest
     ```
   * Host System (Linux/MacOS):
     ```
     python -m venv --system-site-packages ./.venv
     source ./.venv/bin/activate
     pip install -r /path/to/daceri/libs/requirements.txt
     ```
4. Plug in a controller (OS-dependent; usually [Linux](https://www.linuxmint.com/) works the best)
5. Run the RobotController.py file (under the **scripts/** subdirectory) with the desired connection type:
   * Serial (Controller is plugged into the Raspberry Pi):
     ```
     python RobotController.py s
     ```
   * Websockets:
     ```
     python RobotController.py w [R-Pi IPv4 address]
     ```
   * UDP Sockets:
     ```
     python RobotController.py u [R-Pi IPv4 address]
     ```
7. Press the **right** joystick to activate the motors
8. Start moving the joysticks to move the robot!

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

If you can print the gampad's vendor id and product id to the screen but it raises `HIDException` "Unable to open device", that is related to the permission for the device.

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
