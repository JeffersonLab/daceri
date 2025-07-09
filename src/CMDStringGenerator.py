
from REVHubTranslator import REVMotorInputs, REVServoInputs

class CMDStringGnerator:
    """
    Generates command strings for the REV module based on motor and servo inputs.
    """
    def __init__(self):
        self.prev_motor_inputs = REVMotorInputs()
        self.prev_servo_inputs = REVServoInputs()

    def get_cmd_string_list(self, motor_inputs, servo_inputs):
        """
        Generate a list of command strings based on the current motor and servo inputs.
        This method compares the current inputs with the previous inputs and
        generates commands only for those that have changed.
        Args:
            motor_inputs (REVMotorInputs): The current motor inputs.
            servo_inputs (REVServoInputs): The current servo inputs.
        Returns:
            list: A list of command strings to be sent to the REV module.
        """
        res = []
        for motor_input in motor_inputs.inputs:
            if motor_input.speed == self.prev_motor_inputs.inputs[motor_input.mid].speed:
                continue
            res.append(f"set M{str(motor_input.mid + 1)} {str(motor_input.speed)}")

        for servo_key, servo_input in servo_inputs.inputs_dict:
            if servo_input.pos == self.prev_servo_inputs.inputs_dict[servo_key].pos:
                continue
            res.append(f"incr {servo_key} {str(servo_input.pos \
                                               - self.prev_servo_inputs.inputs_dict[servo_key].pos)}")

        # Update the previous inputs with the current ones
        self.prev_motor_inputs = motor_inputs
        self.prev_servo_inputs = servo_inputs

        return res
    
    def send_cmd_string_list_via_websocket(self, socket):
        """
        Send the command strings via a WebSocket connection.
        Args:
            socket (WebSocket): The WebSocket connection to the PI on the robot.
        """
        str_list = self.get_cmd_string_list()
        
        for cmd_string in str_list:
            print(cmd_string)
            pass
