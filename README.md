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
