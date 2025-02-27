"""
Simple code to detect joystick and print its name.

Run this under a Linux OS. Make sure you have installed the required packages:
    pip install pygame evdev approxeng.input

Under a Linux OS, you can either use the commented `pygame` module to detect the
joystick, or the current `approxeng.input` module.

The `pygame` module will work for the MacOS but not `approeng.input`.

You do not need a controller-config.yml file for this code.
"""

# import pygame
# import evdev

# pygame.init()

# # Count the number of joysticks
# joystick_count = pygame.joystick.get_count()

# if joystick_count == 0:
#     print("No joystick detected!")
# else:
#     # Get all available input devices
#     devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

#     for i in range(joystick_count):
#         joystick = pygame.joystick.Joystick(i)
#         joystick.init()

#         name = joystick.get_name()
#         guid = joystick.get_guid()

#         print(f"Joystick {i}: {name}")
#         print(f"  GUID: {guid}")

#         # Find the corresponding /dev/input path
#         for device in devices:
#             if name in device.name:
#                 print(f"  Device Path: {device.path}")

# pygame.quit()

import approxeng.input
from approxeng.input.controllers import find_matching_controllers

controllers = find_matching_controllers()

if controllers:
    for controller in controllers:
        print(f"Joystick detected: {controller}")
        print(f"Device path: {controller.devices}")
else:
    print("No joystick found!")
