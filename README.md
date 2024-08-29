# robot-project
Any code for my robot project in affiliation with Jefferson Lab.

## Run Simulation
1. Download the respective file based on OS and architecture: [https://github.com/google-deepmind/mujoco/releases](https://github.com/google-deepmind/mujoco/releases/latest) 
2. Extract the file, and run **simulate** inside the extracted folder. Mujoco simulator should run
3. Clone this repository
4. Go into the **sim/** directory
5. Drag-and-drop any .xml into the simulator

## Print 3D model parts
1. Clone this repository
2. Go into the **designs/** directory
3. Choose any design you'd like
4. Open in any CAD software and export as STL
5. Use a program like [UltiMaker Cura](https://ultimaker.com/software/ultimaker-cura/) and slice the STL file into GCODE
6. Run on a 3D printer

## Move the robot
1. Clone this repository
2. Go into the **scripts/** directory
4. Use the provided Dockerfile ([Wiki: How to download and install Docker](https://docs.docker.com/get-started/get-docker/)) to automatically setup the correct packages and libraries or use a Linux/MacOS system with Python installed
   * Container:
     ```
     cd ./robot-project
     docker build -t robot-container .
     docker run -v `pwd`:/work/robot:Z -v /dev/input:/dev/input:ro --rm -it robot-container:latest
     ```
   * Host System (Linux/MacOS):
     ```
     python -m ./.venv
     source ./.venv/bin/activate
     pip install -r ./robot-project/libs/requirements.txt
     ```
4. Plug in a controller (OS-dependent, usually [Linux](https://www.linuxmint.com/) works the best)
5. Run the RobotController.py file (under the **scripts/** subdirectory) with the desired connection type:
   * UDP Sockets:
     ```
     python RobotController.py s [R-Pi IPv4 address]
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
