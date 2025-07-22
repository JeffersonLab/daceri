import time
import math
import inputs

# Mock motor controller (replace with real hardware interface)
class Motor:
    def __init__(self, id):
        self.id = id
        self.power = 0.0

    def setPower(self, power):
        print(f"Motor {self.id}: Power set to {round(power, 3)}")
        self.power = power

motors = [Motor(0), Motor(1), Motor(2)]

def move_motor(id, power):
    motors[id].setPower(power)

def main():
    print("Listening for joystick input...")

    last_cmd_time = [0, 0, 0]
    min_cmd_interval = 0.05  # seconds
    last_motor_powers = [0, 0, 0]

    left_joy_H = 0
    left_joy_V = 0
    right_joy_H = 0

    while True:
        # Poll all events from the gamepad
        events = inputs.get_gamepad()
        for event in events:
            if event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    left_joy_H = event.state / 32768.0
                elif event.code == "ABS_Y":
                    left_joy_V = event.state / 32768.0
                elif event.code == "ABS_RX":
                    right_joy_H = event.state / 32768.0

        current_time = time.time()

        # Calculate motor powers
        motor_powers = [0, 0, 0]
        motor_powers[0] = -((2.0 / 3.0) * left_joy_H)
        motor_powers[1] = -((-1.0 / 3.0) * left_joy_H + (1.0 / math.sqrt(3.0)) * left_joy_V)
        motor_powers[2] = -((-1.0 / 3.0) * left_joy_H - (1.0 / math.sqrt(3.0)) * left_joy_V + (1.0 / 3.0) * right_joy_H)

        # Apply deadband
        for i in range(3):
            if abs(motor_powers[i]) < 0.05:
                motor_powers[i] = 0

        # Update motors only if power change is significant and time has passed
        for i in range(3):
            if (
                abs(motor_powers[i] - last_motor_powers[i]) > 0.05 and
                (current_time - last_cmd_time[i]) > min_cmd_interval
            ):
                move_motor(i, motor_powers[i])
                last_motor_powers[i] = motor_powers[i]
                last_cmd_time[i] = current_time

        time.sleep(0.01)  # Small delay to reduce CPU usage

if __name__ == "__main__":
    main()
