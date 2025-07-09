"""
This module provides classes and methods to interface with REVHub motor controllers
and translate GamePad inputs into motor control commands.
"""

import math


MOTOR_NUM = 3
MOTOR_INIT_SPEED = -1.0
MOTOR_POWER_TO_SPEED_FACTOR = 32000

# The pulse width for the servo is in the range of 0.75ms to 2.25ms
SERVO_PULSE_MIN = 0.75
SERVO_PULSE_MAX = 2.25
SERVO_PULSE_RANGE = SERVO_PULSE_MAX - SERVO_PULSE_MIN

class ServoInput:
    """Represents the input for a single servo, including its ID and position."""
    def __init__(self, sid=-1):
        """
        Initialize a ServoInput instance.
        Args:
            sid (int): Servo ID.
        """
        self.sid = sid
        self.pos = 0.0  # the relative position of the servo pulse width

    def get_pulse_width(self, pos):
        """
        Update the pulse width based on the current position.
        """
        return pos * SERVO_PULSE_RANGE + SERVO_PULSE_MIN


class REVServoInputs:
    """Manages inputs for multiple servos on the robot."""
    def __init__(self):
        # Match David's code at
        #  https://github.com/faustus123/HLRobotController/blob/main/scripts/tri_wheel_robot.py
        self.inputs_dict = {}
        for sid in [0, 1, 4, 5]:
            self.inputs_dict['S' + str(sid)] = ServoInput(sid)

    def update_servo_position(self):
        """
        Update the pos for each servo based on GamePad inputs.
        """
        for _, servo_input in self.inputs_dict.items():
            # Ensure the position is within the valid range [0.0, 1.0]
            servo_input.pos = max(servo_input.pos, 0.0)
            servo_input.pos = min(servo_input.pos, 1.0)

    def print_inputs(self):
        """
        Print the current servo inputs, including servo IDs and period increments.
        """
        print("\nServo inputs:")
        for key, servo_input in self.inputs_dict.items():
            print(f"\t{key}: pos={servo_input.pos}")


class MotorInput:
    """Represents the input for a single motor, including its ID and speed."""
    def __init__(self, mid=-1):
        """
        Initialize a MotorInput instance.

        Args:
            mid (int): Motor ID. Valid IDs are 0, 1, and 2. Defaults to -1.
        """
        self.mid = mid  # Motor id. For our robot, the valid motor id can be 0, 1, 2
        # A float number can be negative. Negative number means opposite direction.
        self.speed = MOTOR_INIT_SPEED


class REVMotorInputs:
    """Manages inputs for multiple motors on the robot."""
    def __init__(self):
        """
        Initialize the motor controller inputs with a predefined number of motors.
        """
        self.inputs = []
        for i in range(MOTOR_NUM):
            self.inputs.append(MotorInput(i))

    def print_inputs(self):
        """
        Print the current motor inputs, including motor IDs and speeds.
        """
        for i in self.inputs:
            print(f"Motor input: ID = {i.mid}, Speed = {i.speed}")


class REVHubInputsTranslator:
    """
    Translates GamePad inputs into motor control commands for the REVHub.

    This class processes raw GamePad reports, calculates joystick values,
    and generates motor speed inputs based on the joystick movements.
    """
    def __init__(self):
        """
        Initialize the translator with default states for joystick values
        and motor inputs.
        """
        self.raw_state = {}
        self.last_joy_values = [-1.0, -1.0, -1.0, -1.0]
        self.curr_joy_values = self.last_joy_values

        self.last_motor_speeds = [MOTOR_INIT_SPEED , MOTOR_INIT_SPEED , MOTOR_INIT_SPEED ]
        self.curr_motor_inputs = REVMotorInputs()

        self.curr_servo_inputs = REVServoInputs()

    def get_raw_state_from_report(self, gpd_report):
        """
        Parse the raw GamePad report and update the internal state.

        Args:
            gpd_report (list): A list of bytes representing the GamePad report.
        """
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
        """
        Check if servo inputs are enabled based on the GamePad state.
        """
        if self.raw_state['R3']:
            print("\nEnable all servos\n")

    def is_motor_inputs_enabled(self):
        """
        Check if motor inputs are enabled based on the GamePad state.
        """
        if self.raw_state['L3']:
            print("\nEnable all motors\n")

    def print_report_n_state(self, report):
        """
        Print the GamePad report and the parsed raw state.

        Args:
            report (list): A list of bytes representing the GamePad report.
        """
        print(report)
        self.get_raw_state_from_report(report)
        print(self.raw_state)

    def get_servo_inputs(self, print_input=False):
        """
        Update the servo inputs based on the GamePad state.
        """
        # Servo 0: S0
        if self.raw_state['dpad_up']:
            self.curr_servo_inputs.inputs_dict['S0'].pos += 0.01
        if self.raw_state['dpad_down']:
            self.curr_servo_inputs.inputs_dict['S0'].pos -= 0.01
        # Servo 1: S1
        if self.raw_state['dpad_left']:
            self.curr_servo_inputs.inputs_dict['S1'].pos += 0.01
        if self.raw_state['dpad_right']:
            self.curr_servo_inputs.inputs_dict['S1'].pos -= 0.01
        # Servo 4: S4
        if self.raw_state['button_Y']:
            self.curr_servo_inputs.inputs_dict['S4'].pos += 0.01
        if self.raw_state['button_A']:
            self.curr_servo_inputs.inputs_dict['S4'].pos -= 0.01
        # Servo 5: S5
        if self.raw_state['button_X']:
            self.curr_servo_inputs.inputs_dict['S5'].pos += 0.01
        if self.raw_state['button_B']:
            self.curr_servo_inputs.inputs_dict['S5'].pos -= 0.01

        # Update the pulse width for each servo based on its neew position
        self.curr_servo_inputs.update_servo_position()

        if print_input:
            self.curr_servo_inputs.print_inputs()

    def get_curr_joy_values(self):
        """
        Update the current joystick values based on the raw GamePad state.
        """
        def get_gamepad_joy_value_from_report(key_str):
            return self.raw_state[key_str] if abs(self.raw_state[key_str]) >= 0.05 else 0.0

        for i, key_string in enumerate(['left_joy_V', 'left_joy_H', 'right_joy_V', 'right_joy_H']):
            self.curr_joy_values[i] = get_gamepad_joy_value_from_report(key_string)

    def get_curr_motor_speed_from_joy_values(self, print_value=False):
        """
        Calculate motor speeds based on the current joystick values.

        Args:
            print_value (bool): Whether to print the joystick values. Defaults to False.

        Returns:
            list: A list of motor speeds calculated from joystick inputs.e with a REV module using the REV communication protocol.
        """
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
        """
        Updates motor inputs based on the current speeds and joystick values.

        This method adjusts the motor speeds and joystick values to ensure smooth
        transitions and updates the motor inputs accordingly. It also provides an
        option to print the motor inputs for debugging purposes.

        Args:
            curr_speeds (list[float]): A list of current motor speeds.
            print_input (bool): A flag to indicate whether to print the motor inputs.

        Behavior:
            - If the absolute value of a motor speed is less than 0.05, it is set to 0.0.
            - If the difference between the current and previous motor speeds exceeds 0.05,
              the motor speed is updated.
            - Motor 2 (the third motor) is controlled by the right joystick's horizontal (H) value.
              If the joystick value changes by more than 0.05, the motor speed is updated.
            - Optionally prints the motor inputs if `print_input` is True.
        """
        # if print_input:
        #     print(f"Before: curr_speed={curr_speeds}, prev_speed={self.last_motor_speeds}")

        for i in range(MOTOR_NUM):
            if abs(curr_speeds[i]) < 0.05:
                curr_speeds[i] = 0.0

            if abs(curr_speeds[i] - self.last_motor_speeds[i]) > 0.05:
                self.last_motor_speeds[i] = curr_speeds[i]
                self.curr_motor_inputs.inputs[i].speed = self.last_motor_speeds[i]

        # Motor 2 (the third motor) is controlled by the right joystick's H value.
        if abs(self.curr_joy_values[3] - self.last_joy_values[3]) > 0.05:
            self.last_joy_values[3] = self.curr_joy_values[3]
            self.last_motor_speeds[2] = self.last_joy_values[3]

        if print_input:
            # print(f"After: curr_speed={curr_speeds}, prev_speed={self.last_motor_speeds}")
            self.curr_motor_inputs.print_inputs()


    def get_motor_inputs(self, print_input=False):
        "Genrate motor inputs based on the current GamePad report."
        curr_motor_speeds = self.get_curr_motor_speed_from_joy_values(print_input)
        self.get_motor_inputs_from_speeds(curr_motor_speeds, print_input)
