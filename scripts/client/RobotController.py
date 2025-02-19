# This script is run on the client's machine to communicate with the websockets server on the robot.
# It sends a network command which the server will interpret
# and then send a serial input into the motor controller.
# Local serial is also available, so one can control the robot nearby with a hard-wired connection.

import serial
import socket
import websocket
import inputs
from inputs import get_gamepad
from inputs import get_key
import time
import math
import sys
import os
import subprocess
import threading
import platform

from datetime import datetime
from approxeng.input.selectbinder import ControllerResource
from approxeng.input.controllers import find_matching_controllers
from approxeng.input.dualshock4 import DualShock4
from approxeng.input.controllers import ControllerRequirement

class DetermineInput():
	def __init__(self):
		if len(sys.argv) > 1:
			self.config = sys.argv[1]
			print("Setting config to: %s" % self.config)

			DetermineInput.Setup(self.config)

	def Setup(config):
		if config == "s" or config == "S":
			serial = Serial()
			if platform.system() == 'Linux':
				ControllerSupportApproxEngLib(config)
			elif platform.system() == 'Darwin':
				ControllerSupportHID(config)
		elif config == "w" or config == "W":
			web = WebSocket()
			if platform.system() == 'Linux':
				ControllerSupportApproxEngLib(config)
			elif platform.system() == 'Darwin':
				ControllerSupportHID(config)
		elif config == "u" or config == "U":
			udp = UDP()
			if platform.system() == 'Linux':
				ControllerSupportApproxEngLib(config)
			elif platform.system() == 'Darwin':
				ControllerSupportHID(config)

class UDP():
	UDP_IP = "192.168.1.42"
	UDP_PORT = 5005

	def __init__(self):
		UDP.UDP_IP = "192.168.1.42"
		UDP.UDP_PORT = 5005

		if len(sys.argv) > 1:
			UDP.UDP_IP = sys.argv[2]

		print("UDP target IP: %s" % UDP.UDP_IP)
		print("UDP target port: %s" % UDP.UDP_PORT)

		global sock
		sock = socket.socket(socket.AF_INET, # Internet
				     socket.SOCK_DGRAM) # UDP

	def SetEnableAllUDP(val):
		for i in range(4): sock.sendto(("enable M" + str(i) + " " + str(val)).encode(), (UDP.UDP_IP,UDP.UDP_PORT))
		for i in range(8): sock.sendto(("enable S" + str(i) + " " + str(val)).encode(), (UDP.UDP_IP,UDP.UDP_PORT))

	def send(cmd):
		sock.sendto(cmd.encode(), (UDP.UDP_IP,UDP.UDP_PORT))

class WebSocket():
	host = "192.168.1.42"
	port = "5000"
	def __init__(self):
		WebSocket.host = "192.168.1.42"
		WebSocket.port = "5000"

		if len(sys.argv) > 1:
			WebSocket.host = sys.argv[2]
		print("Setting host to: %s" % WebSocket.host)
		threading.Thread(target=WebSocket.WSThread).start()
		last_move_command_send_time = datetime.now()

	def on_ws_message(ws, message):
		# print(f"Received '{message}'")
		pass

	def on_ws_error(ws, error):
		print(f"Error: {error}")

	def on_ws_close(ws, close_status_code, close_msg):
		print("### closed ###")

	def on_ws_open(ws):
		print("Connection established")
		# ws.send("Hello ESP8266")

	def WSThread():
		global ws
		ws = websocket.WebSocketApp("ws://" + WebSocket.host + ":" + WebSocket.port + "/",
								on_open=WebSocket.on_ws_open,
								on_message=WebSocket.on_ws_message,
								on_error=WebSocket.on_ws_error,
								on_close=WebSocket.on_ws_close)
		print("Websockets thread started.")
		ws.run_forever()

	def SetEnableAllWebSockets(val):
		for i in range(4): ws.send("enable M" + str(i) + " " + str(val))
		for i in range(8): ws.send("enable S" + str(i) + " " + str(val))

class Serial():
	def __init__(self):
		global ser
		Serial.address = "/dev/ttyUSB0"
		if len(sys.argv) > 1:
			Serial.address = sys.argv[2]
			ser = serial.Serial(Serial.address, 115200)
		else:
			ser = serial.Serial(Serial.address, 115200)
		print("Setting up serial, please wait...")
		time.sleep(2)  # Wait for the serial connection to initialize

	#-------------------------------------
	# SetEnableAllSerial - Only runs on serial
	#-------------------------------------
	def SetEnableAllSerial(value):
		ser.write(("enable M0 " + str(value)+ '\n').encode())
		ser.write(("enable M1 " + str(value)+ '\n').encode())
		ser.write(("enable M2 " + str(value)+ '\n').encode())
		ser.write(("enable M3 " + str(value)+ '\n').encode())

		ser.write(("enable S0 " + str(value)+ '\n').encode())
		ser.write(("enable S1 " + str(value)+ '\n').encode())
		ser.write(("enable S2 " + str(value)+ '\n').encode())
		ser.write(("enable S3 " + str(value)+ '\n').encode())
		ser.write(("enable S4 " + str(value)+ '\n').encode())
		ser.write(("enable S5 " + str(value)+ '\n').encode())
		ser.write(("enable S6 " + str(value)+ '\n').encode())
		ser.write(("enable S7 " + str(value)+ '\n').encode())

	def WriteToSerial(msg):
		ser.write((msg).encode())
		#while ser.in_waiting > 0:
			#response = ser.readline().decode('utf-8').rstrip()
			#print(f"ESP32 Response: {response}")

#-------------------------------------
# ControllerSupportApproxEngLib - Robot-specific input library
#-------------------------------------
def ControllerSupportApproxEngLib(flag):

	last_R3 = False
	last_L3 = False
	last_left_joy_V = -1
	last_left_joy_H = -1
	last_right_joy_V = -1
	last_right_joy_H = -1

	left_joy_V = 0
	left_joy_H = 0
	right_joy_V = 0
	right_joy_H = 0

	last_P1 = -1
	last_P2 = -1
	last_P3 = -1

	P1 = 0
	P2 = 0
	P3 = 0
	P4 = 0
	#discoveries = find_matching_controllers()
	try:
		with ControllerResource(ControllerRequirement(require_class=DualShock4)) as joystick:
			print('Found a joystick and connected')
			while joystick.connected:
				presses = joystick.check_presses()
				lx, ly = joystick['l']
				rx, ry = joystick['r']
				ls = joystick['ls']
				rs = joystick['rs']
				a = joystick['cross']
				x = joystick['square']
				c = joystick['circle']
				t = joystick['triangle']
				l1 = joystick['l1']
				r1 = joystick['r1']
				dup = joystick['dup']
				ddown = joystick['ddown']
				dleft = joystick['dleft']
				dright = joystick['dright']

				if presses['ls']:
					if flag == "s":
						Serial.SetEnableAllSerial(0)
					elif flag == "w":
						WebSocket.SetEnableAllWebSockets(0)
					elif flag == "u":
						UDP.SetEnableAllUDP(0)
				if presses['rs']:
					if flag == "s":
						Serial.SetEnableAllSerial(1)
					elif flag == "w":
						WebSocket.SetEnableAllWebSockets(1)
					elif flag == "u":
						UDP.SetEnableAllUDP(1)
				#if joystick.releases.ddown:
				power = 1
				if presses['square']:
					if x is not None:
						power = 0.5
				elif presses['cross']:
					if a is not None:
						power = 1.2
				elif presses['dup']:
					if dup is not None:
						cmd = "set S4 .05"
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)
				elif presses['ddown']:
					if ddown is not None:
						cmd = "set S4 -.05"
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)
				elif presses['dleft']:
					if dleft is not None:
						cmd = "set S3 -.05"
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)
				elif presses['dright']:
					if dright is not None:
						cmd = "set S3 .05"
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

				P1 = -(2.0/3.0)*lx+(1.0/3.0)*rx
				P2 = (1.0/3.0)*lx+(1.0/math.sqrt(3.0))*ly+(1.0/3.0)*rx
				P3 = (1.0/3.0)*lx-(1.0/math.sqrt(3.0))*ly+(1.0/3.0)*rx
#				P1 = (-1)*lx+(1.0/3.0)*rx
#				P2 = (1.0/2.0)*lx+(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
#				P3 = (1.0/2.0)*lx-(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
#				Increase power if needed
				P1 = -power*P1
				P2 = -power*P2
				P3 = -power*P3

#				print("=======")
#				print("P1:", P1)
#				print("P2:", P2)
#				print("P3:", P3)
#				print("=======")
#				print("ly:", ly)

				if( abs(P1 ) < 0.15 ) :  P1 = 0
				if( abs(P2 ) < 0.15 ) :  P2 = 0
				if( abs(P3 ) < 0.15 ) :  P3 = 0

				deadzone = 0.05
				if (P4 == 0):
					if( abs( P1 - last_P1 ) > deadzone ):
						last_P1 = P1
						cmd = "set M0 " + str(P1)
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

					if( abs( P2 - last_P2 ) > deadzone ):
						last_P2 = P2
						cmd = "set M1 " + str(P2)
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

					if( abs( P3 - last_P3 ) > deadzone ):
						last_P3 = P3
						cmd = "set M3 " + str(P3) # M3 is connected to the M2 slot
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

				# We need to check the other motors when we try to turn on the drum motor so as to not burn out the L298N!

				if presses['l1']:
					if l1 is not None:
						P4 = 5
						if (P1 == 0 and P2 == 0 and P3 == 0):
							cmd = "set M2 " + str(P4)
							if flag == "s":
								Serial.WriteToSerial(cmd + '\n')
							elif flag == "w":
								ws.send(cmd)
							elif flag == "u":
								UDP.send(cmd)

				if presses['r1']:
					if r1 is not None:
						P4 = -5
						if (P1 == 0 and P2 == 0 and P3 == 0):
							cmd = "set M2 " + str(P4)
							if flag == "s":
								Serial.WriteToSerial(cmd + '\n')
							elif flag == "w":
								ws.send(cmd)
							elif flag == "u":
								UDP.send(cmd)

				if presses['circle']:
					if c is not None:
						P4 = 0
						S0 = 0
						S1 = 0
						cmd = "set M2 " + str(P4) + '\n' + "set S0 " + str(S0) + '\n' "set S1 " + str(S1)
						if flag == "s":
							Serial.WriteToSerial(cmd + '\n')
						elif flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)
		# Joystick disconnected...
		print('Connection to joystick lost')
	except IOError:
		# No joystick found, wait for a bit before trying again
		print('Unable to find any joysticks')
		time.sleep(1.0)

def LogitechGameControllerHIDReport(report):
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

def ControllerSupportHID(config):
	vendor_id = 0x0
	product_id = 0x0
	gamepad = None
	state = None
	for d in hid.enumerate():
		if d['product_string'] == 'Logitech Dual Action':
			vendor_id  = int(d['vendor_id' ])
			product_id = int(d['product_id'])
			print('Found Logictech gamepad: vendor_id:0x%x product_id:0x%x' % (vendor_id, product_id))
			gamepad = hid.Device(vid=vendor_id, pid=product_id)
			gamepad.nonblocking = True
	#		gamepad = hid.device()
	#		gamepad.open(vendor_id, product_id)
	#		gamepad.set_nonblocking(True)
	if not gamepad:
		print('Unable to find gamepad!')
	else:
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
			report = gamepad.read(512)
			if report:
				state = LogitechReportToState(report)
			else:
				#state = None
				time.sleep(0.050)
				#print('Unable to get controller state')
			if state:
				message = ''

				if state['L3']: SetEnableAll(0)
				if state['R3']: SetEnableAll(1)

#				if state['dpad_up'   ]: ws.send("incr S0  0.01")
#				if state['dpad_down' ]: ws.send("incr S0 -0.01")
#				if state['dpad_left' ]: ws.send("incr S1  0.01")
#				if state['dpad_right']: ws.send("incr S1 -0.01")
#
#				if state['button_Y'  ]: ws.send("incr S4  0.01")
#				if state['button_A'  ]: ws.send("incr S4 -0.01")
#				if state['button_X'  ]: ws.send("incr S5  0.01")
#				if state['button_B'  ]: ws.send("incr S5 -0.01")


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
					cmd = "set M0 " + str(P1)
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					elif flag == "w":
						ws.send(cmd)
					elif flag == "u":
						UDP.send(cmd)

				if( abs( P2 - last_P2 ) > 0.05 ):
					last_P2 = P2
					cmd = "set M1 " + str(P2)
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					elif flag == "w":
						ws.send(cmd)
					elif flag == "u":
						UDP.send(cmd)

				if( abs( P3 - last_P3 ) > 0.05 ):
					last_P3 = P3
					cmd = "set M3 " + str(P3) # M3 is connected to the M2 slot
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					elif flag == "w":
						ws.send(cmd)
					elif flag == "u":
						UDP.send(cmd)

				if message : print(message)
				message = None

#def KeyboardSupport():
#	# TODO

if __name__ == "__main__":
	DetermineInput()
