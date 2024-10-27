# Script taken from: https://github.com/shillehbean/youtube-p2/blob/main/mpu6050_test.py

from mpu6050 import mpu6050
import smbus
import time

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Create a new Mpu6050 object
mpu6050 = mpu6050.mpu6050(0x68)

# Define a function to read the sensor data
def read_sensor_data():
    # Read the accelerometer values
    accelerometer_data = mpu6050.get_accel_data()

    # Read the gyroscope values
    gyroscope_data = mpu6050.get_gyro_data()

    # Read temp
    temperature = mpu6050.get_temp()

    return accelerometer_data, gyroscope_data, temperature

# Start a while loop to continuously read the sensor data
while True:

    # Read the sensor data
    accelerometer_data, gyroscope_data, temperature = read_sensor_data()

    # Print the sensor data
    # An accelerometer is a device that measures the proper acceleration of an object
    # Proper acceleration is the acceleration of the object relative to an observer who is in free fall
    print(color.UNDERLINE + color.CYAN + "Accelerometer data:" + color.END, accelerometer_data)

    # A gyroscope is a device used for measuring or maintaining orientation and angular velocity
    # It is a spinning wheel or disc in which the axis of rotation is free to assume any orientation by itself
    print(color.UNDERLINE + color.GREEN + "Gyroscope data (orientation):" + color.END, gyroscope_data)

    print(color.UNDERLINE + color.RED + "Temperature:" + color.END, temperature)

    print("===")

    # Wait for 1 second
    time.sleep(1)
