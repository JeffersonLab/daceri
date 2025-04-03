"""
"""

import math


MOTOR_NUM = 3
MOTOR_INIT_SPEED = -1.0


class MotorInput:
    "Input for one Motor"
    def __init__(self, mid=-1):
        self.mid = mid  # Motor id. For our robot, the valid motor id can be 0, 1, 2
        # A float number can be negative. Negative number means opposite direction.
        self.speed = MOTOR_INIT_SPEED


class REVMotorControllerInputs:
    "Inputs for the three motors on the robot."

    def __init__(self):
        self.motors = []
        for i in range(MOTOR_NUM):
            self.motors.append(MotorInput(i))

    def print_inputs(self):
        "Print the Motor Controller inputs to the screen"
        for i, motor in enumerate(self.motors):
            print(f"Motor input: ID = {motor.mid}, Speed = {motor.speed}")


class REVHubInputsTranslator:
    """
    Translate the GamePad inputs to REVHub Motor and inputs.
    """
    def __init__(self):
        self.raw_state = {}
        self.last_joy_values = [-1.0, -1.0, -1.0, -1.0]
        self.curr_joy_values = self.last_joy_values

        self.last_motor_speeds = [MOTOR_INIT_SPEED , MOTOR_INIT_SPEED , MOTOR_INIT_SPEED ]
        self.curr_motor_inputs = REVMotorControllerInputs()

    def get_raw_state_from_report(self, gpd_report):
        "Get the raw state from the gamepad inputs."
        self.raw_state['left_joy_H'] = max( (float(gpd_report[0])-128.0)/127.0, -1.0)
        self.raw_state['left_joy_V'] = max( (float(gpd_report[1])-128.0)/127.0, -1.0)
        self.raw_state['right_joy_H'] = max( (float(gpd_report[2])-128.0)/127.0, -1.0)
        self.raw_state['right_joy_V'] = max( (float(gpd_report[3])-128.0)/127.0, -1.0)
        dpad = gpd_report[4] & 0b00001111
        self.raw_state['dpad_up'   ] = (dpad==0) or (dpad==1) or (dpad==7)
        self.raw_state['dpad_down' ] = (dpad==3) or (dpad==4) or (dpad==5)
        self.raw_state['dpad_left' ] = (dpad==5) or (dpad==6) or (dpad==7)
        self.raw_state['dpad_right'] = (dpad==1) or (dpad==2) or (dpad==3)
        self.raw_state['button_X'] = (gpd_report[4] & 0b00010000) != 0
        self.raw_state['button_A'] = (gpd_report[4] & 0b00100000) != 0
        self.raw_state['button_B'] = (gpd_report[4] & 0b01000000) != 0
        self.raw_state['button_Y'] = (gpd_report[4] & 0b10000000) != 0
        self.raw_state['bumper_left'  ] = (gpd_report[5] & 0b00000001) != 0
        self.raw_state['bumper_right' ] = (gpd_report[5] & 0b00000010) != 0
        self.raw_state['trigger_left' ] = (gpd_report[5] & 0b00000100) != 0
        self.raw_state['trigger_right'] = (gpd_report[5] & 0b00001000) != 0
        self.raw_state['back'         ] = (gpd_report[5] & 0b00010000) != 0
        self.raw_state['start'        ] = (gpd_report[5] & 0b00100000) != 0
        self.raw_state['L3'           ] = (gpd_report[5] & 0b01000000) != 0
        self.raw_state['R3'           ] = (gpd_report[5] & 0b10000000) != 0

        self.is_motor_inputs_enabled()
        self.is_servo_inputs_enabled()

    def is_servo_inputs_enabled(self):
        if self.raw_state['R3']:
            print("\tEnable all servos")

    def is_motor_inputs_enabled(self):
        if self.raw_state['L3']:
            print("\tEnable all motors")

    def print_report_n_state(self, report):
        """Print the GamePad input as a byte string."""
        print(report)
        self.get_raw_state_from_report(report)
        print(self.raw_state)

    def get_curr_joy_values(self):
        """Get the joy values (floating-point numbers) from the GamePad report."""
        def get_gamepad_joy_value_from_report(key_str):
            return self.raw_state[key_str] if abs(self.raw_state[key_str]) >= 0.05 else 0.0

        for i, key_string in enumerate(['left_joy_V', 'left_joy_H', 'right_joy_V', 'right_joy_H']):
            self.curr_joy_values[i] = get_gamepad_joy_value_from_report(key_string)

    def get_curr_motor_speed_from_joy_values(self, print_value=False):
        self.get_curr_joy_values()
        if print_value:
            print(f"\nJoy values: pre={self.last_joy_values}, curr={self.curr_joy_values}")

        # joy_values[0-3]: 'left_joy_V', 'left_joy_H', 'right_joy_V', 'right_joy_H'
        return [
            -2.0/3.0 * self.curr_joy_values[1] - 1.0/3.0 * self.curr_joy_values[3],
            1.0/3.0 * self.curr_joy_values[1] - 1.0/math.sqrt(3.0) * self.curr_joy_values[0]
                - 1.0/3.0 * self.curr_joy_values[3],
            1.0/3.0 * self.curr_joy_values[1] + 1.0/math.sqrt(3.0) * self.curr_joy_values[0]
                - 1.0/3.0 * self.curr_joy_values[3]
        ]

    def get_motor_inputs_from_speeds(self, curr_speeds, print_input):
        # if print_input:
        #     print(f"Before: curr_speed={curr_speeds}, prev_speed={self.last_motor_speeds}")

        for i in range(MOTOR_NUM):
            if abs(curr_speeds[i]) < 0.05:
                curr_speeds[i] = 0.0

            if abs(curr_speeds[i] - self.last_motor_speeds[i]) > 0.05:
                self.last_motor_speeds[i] = curr_speeds[i]
                self.curr_motor_inputs.motors[i].speed = self.last_motor_speeds[i]

        # Motor 2 (the third motor) is controlled by the right joystick's H value.
        if abs(self.curr_joy_values[3] - self.last_joy_values[3]) > 0.05:
            self.last_joy_values[3] = self.curr_joy_values[3]
            self.last_motor_speeds[2] = self.last_joy_values[3]

        if print_input:
            # print(f"After: curr_speed={curr_speeds}, prev_speed={self.last_motor_speeds}")
            self.curr_motor_inputs.print_inputs()


    def get_motor_control_input(self, print_input=False):
        "Genrate motor inputs based on the current GamePad report."
        curr_motor_speeds = self.get_curr_motor_speed_from_joy_values(print_input)
        self.get_motor_inputs_from_speeds(curr_motor_speeds, print_input)
