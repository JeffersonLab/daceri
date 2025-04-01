"""
# This is an example of how to detect a Logitech F310 Game Controller connected to the local host.
#
# This requires a few python packages and the underlying system-level hdapi support.
#
# Install the uderlying system-level hidapi support. The process has been tested on a RHEL 8.6
# (Linux 4.8 kernel) and MacOS 15.3.2.
#
# For RHEL Linux OS
# 1. sudo dnf groupinstall "Development Tools"
# 2. sudo dnf install libusb-devel
# 3. Install hid library to /usr/local via the submodule external/hidapi cmake
# 4. nm -D /usr/local/lib/libhidapi-hidraw.so | grep hid_get_input_report
# 5. export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
#
# For MacOS: brew install hidapi. Do not need to install the hidapi submodule.
#
# For pyvenv, it is recommended to install them in a virtual environment like this:
# python3 -m venv venv
# source venv/bin/activate
# pip install --upgrade pip
# pip install hid
#
#-----------------------------------------------------------------
# Controls:
#
# push in the right joystick to enable all channels.
# push in the left joystick to disable all channels.
#
# Left  joystick controls M0(vertical) and M1(horizontal)
# Right joystick controls M2(vertical) and M3(horizontal)
#
# DPad up/down controls S0
# DPad left/right controls S1
#
# Buttons Y,A control S4
# Buttons X,B control S5
"""

import math
import threading
import time
import sys
import os
import subprocess
import hid
from datetime import datetime


#-------------------------------------
# LogitechReportToState
#-------------------------------------
def get_gamepad_state(report):
    """
    Convert a report from the Logitech game controller to a state dictionary.
    """
    state = {}
    state['left_joy_H'] = max( (float(report[0])-128.0)/127.0, -1.0)
    state['left_joy_V'] = max( (float(report[1])-128.0)/127.0, -1.0)
    state['right_joy_H'] = max( (float(report[2])-128.0)/127.0, -1.0)
    state['right_joy_V'] = max( (float(report[3])-128.0)/127.0, -1.0)
    dpad = report[4] & 0b00001111
    state['dpad_up'   ] = (dpad==0) or (dpad==1) or (dpad==7)
    state['dpad_down' ] = (dpad==3) or (dpad==4) or (dpad==5)
    state['dpad_left' ] = (dpad==5) or (dpad==6) or (dpad==7)
    state['dpad_right'] = (dpad==1) or (dpad==2) or (dpad==3)
    state['button_X'] = (report[4] & 0b00010000) != 0
    state['button_A'] = (report[4] & 0b00100000) != 0
    state['button_B'] = (report[4] & 0b01000000) != 0
    state['button_Y'] = (report[4] & 0b10000000) != 0
    state['bumper_left'  ] = (report[5] & 0b00000001) != 0
    state['bumper_right' ] = (report[5] & 0b00000010) != 0
    state['trigger_left' ] = (report[5] & 0b00000100) != 0
    state['trigger_right'] = (report[5] & 0b00001000) != 0
    state['back'         ] = (report[5] & 0b00010000) != 0
    state['start'        ] = (report[5] & 0b00100000) != 0
    state['L3'           ] = (report[5] & 0b01000000) != 0
    state['R3'           ] = (report[5] & 0b10000000) != 0
    return state


#-------------------------------------
# SetEnableAll
#-------------------------------------
def set_gamepad_enable_all(val):
    for i in range(4):
        print("enable M" + str(i) + " " + str(val))
    for i in range(8):
        print("enable S" + str(i) + " " + str(val))


# Setup HID (game controller)
# Find Logitech device
def get_gamepad():
    """
    Find the Logitech game controller and return the device object.
    """
    gamepad = None
    for d in hid.enumerate():
        if d['product_string'] == 'Logitech Dual Action':
            # print(f"vid={d['vendor_id' ]}, pid={d['product_id']}, path={d['path']}")
            vendor_id  = int(d['vendor_id' ])
            product_id = int(d['product_id'])
            path = d['path']
            print('Found Logictech gamepad: vendor_id: [0x%x], product_id:[0x%x]'%(vendor_id, product_id))
            # NOTE: Check the path permission if there is HID "Unable to open device" error
            gamepad = hid.Device(path=path)
            gamepad.nonblocking = True
    return gamepad


#-------------------------------------
# Main
#-------------------------------------
gpad = get_gamepad()
if gpad is None:
    print('Unable to find gamepad!')
    sys.exit(2)
else:
    state = None
    last_R3 = False
    last_L3 = False
    last_left_joy_V = -1
    last_left_joy_H = -1
    last_right_joy_V = -1
    last_right_joy_H = -1

    last_P1 = -1
    last_P2 = -1
    last_P3 = -1

    while True:
        report = gpad.read(512)
        if report:
            state = get_gamepad_state(report)
        else:
            time.sleep(1)
            print('Unable to get controller state')

        if state:
            message = ''
            if state['L3']:
                set_gamepad_enable_all(0)
            if state['R3']:
                set_gamepad_enable_all(1)

            if state['dpad_up'   ]: print("incr S0  0.01")
            if state['dpad_down' ]: print("incr S0 -0.01")
            if state['dpad_left' ]: print("incr S1  0.01")
            if state['dpad_right']: print("incr S1 -0.01")

            if state['button_Y'  ]: print("incr S4  0.01")
            if state['button_A'  ]: print("incr S4 -0.01")
            if state['button_X'  ]: print("incr S5  0.01")
            if state['button_B'  ]: print("incr S5 -0.01")

            # For the joysticks we implement a deadband around zero
            # as well as the last value sent. This significantly 
            # reduces the number of messages sent.
            left_joy_V = state['left_joy_V']
            left_joy_H = state['left_joy_H']
            right_joy_V = state['right_joy_V']
            right_joy_H = state['right_joy_H']

            if( abs(left_joy_V ) < 0.05 ) :  left_joy_V  = 0
            if( abs(left_joy_H ) < 0.05 ) :  left_joy_H  = 0
            if( abs(right_joy_V) < 0.05 ) :  right_joy_V = 0
            if( abs(right_joy_H) < 0.05 ) :  right_joy_H = 0

            P1 = (2.0/3.0)*left_joy_H+(1.0/3.0)*right_joy_H
            P2 = (-1.0/3.0)*left_joy_H+(1.0/math.sqrt(3.0))*left_joy_V+(1.0/3.0)*right_joy_H
            P3 = (-1.0/3.0)*left_joy_H-(1.0/math.sqrt(3.0))*left_joy_V+(1.0/3.0)*right_joy_H

            # # Motors are reversed
            P1 = -P1
            P2 = -P2
            P3 = -P3

            if( abs(P1 ) < 0.05 ) :  P1 = 0
            if( abs(P2 ) < 0.05 ) :  P2 = 0
            if( abs(P3 ) < 0.05 ) :  P3 = 0

            if( abs( P1 - last_P1 ) > 0.05 ):
                last_P1 = P1
                cmd = "set M1 " + str(P1)
                print(cmd)
            if( abs( P2 - last_P2 ) > 0.05 ):
                last_P2 = P2
                cmd = "set M2 " + str(P2)
                print(cmd)
            if( abs( P3 - last_P3 ) > 0.05 ):
                last_P3 = P3
                cmd = "set M3 " + str(P3)
                print(cmd)
            if( abs( right_joy_H - last_right_joy_H ) > 0.05 ):
                last_right_joy_H = right_joy_H
                cmd = "set M3 " + str(last_right_joy_H)
                print(cmd)
            if message:
                print(message)

            message = None
