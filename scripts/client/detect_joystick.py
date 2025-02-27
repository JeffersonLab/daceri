"""
Simple code to detect joystick and print its name.

Run this under a Linux OS. Make sure you have installed the required packages:

pip install pygame evdev
"""

import pygame
import evdev

pygame.init()

# Count the number of joysticks
joystick_count = pygame.joystick.get_count()

if joystick_count == 0:
    print("No joystick detected!")
else:
    # Get all available input devices
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        name = joystick.get_name()
        guid = joystick.get_guid()

        print(f"Joystick {i}: {name}")
        print(f"  GUID: {guid}")

        # Find the corresponding /dev/input path
        for device in devices:
            if name in device.name:
                print(f"  Device Path: {device.path}")

pygame.quit()
