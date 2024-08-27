# This script is run on the client's machine to communicate with the websockets server on the robot.
# It sends a websockets command which the websockets server will interpret
# and then send a serial input into the motor controller.

import serial
import socket
import inputs
import time
import math
import sys
import os
import subprocess
import threading
from sys import platform
from inputs import get_gamepad
from inputs import get_key
from datetime import datetime

from approxeng.input.selectbinder import ControllerResource

import websocket

class DetermineInput():
	def __init__(self):
		if len(sys.argv) > 1:
			self.config = sys.argv[1]
			print("Setting config to: %s" % self.config)

			DetermineInput.Setup(self.config)

	def Setup(config):
		if config == "s" or config == "S":
			serial = Serial("/dev/ttyUSB0")
			ControllerSupportApproxEngLib(config)
		elif config == "w" or config == "W":
			web = WebSocket()
			ControllerSupportApproxEngLib(config)
		elif config == "u" or config == "U":
			udp = UDP()
			ControllerSupportApproxEngLib(config)

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
	def __init__(self, path):
		if len(sys.argv) > 1:
			self.ser = serial.Serial("/dev/" + path, 115200)
		else:
			self.ser = serial.Serial("/dev/TTYUSB0" + path, 115200)
		print("Setting up serial, please wait...")
		time.sleep(2)  # Wait for the serial connection to initialize

	#-------------------------------------
	# SetEnableAllSerial - Only runs on serial
	#-------------------------------------
	def SetEnableAllSerial(value):
		Serial.ser.write(("enable M0 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable M1 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable M2 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable M3 " + str(value)+ '\n').encode())

		Serial.ser.write(("enable S0 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S1 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S2 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S3 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S4 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S5 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S6 " + str(value)+ '\n').encode())
		Serial.ser.write(("enable S7 " + str(value)+ '\n').encode())

	def WriteToSerial(msg):
		Serial.ser.write((msg).encode())
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
	try:
		with ControllerResource() as joystick:
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

				if presses['cross']:
					if a is not None:
						cmd = "set M2 5"
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)


				if presses['square']:
					if x is not None:
						cmd = "set M2 -5"
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

				if presses['circle']:
					if c is not None:
						cmd = "set M2 0"
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)


				P1 = (-1)*lx+(1.0/3.0)*rx
				P2 = (1.0/2.0)*lx+(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
				P3 = (1.0/2.0)*lx-(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
#				Increase power if needed
				power = 1.1
				P1 = power*P1
				P2 = power*P2
				P3 = power*P3

#				print("=======")
#				print("P1:", P1)
#				print("P2:", P2)
#				print("P3:", P3)
#				print("=======")
#				print("ly:", ly)

				if( abs(P1 ) < 0.15 ) :  P1 = 0
				if( abs(P2 ) < 0.15 ) :  P2 = 0
				if( abs(P3 ) < 0.15 ) :  P3 = 0

#				if (abs(ly) > 0.9 and abs(lx) < 0.1):
#					P1 = 0
#					P2 = -2
#					P3 = 2

				deadzone = 0.05
				if( abs( P1 - last_P1 ) > deadzone ):
					last_P1 = P1
					cmd = "set M0 " + str(P1)
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					else:
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

				if( abs( P2 - last_P2 ) > deadzone ):
					last_P2 = P2
					cmd = "set M1 " + str(P2)
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					else:
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)

				if( abs( P3 - last_P3 ) > deadzone ):
					last_P3 = P3
					cmd = "set M3 " + str(P3) # M3 is connected to the M2 slot
					if flag == "s":
						Serial.WriteToSerial(cmd + '\n')
					else:
						if flag == "w":
							ws.send(cmd)
						elif flag == "u":
							UDP.send(cmd)
		# Joystick disconnected...
		print('Connection to joystick lost')
	except IOError:
		# No joystick found, wait for a bit before trying again
		print('Unable to find any joysticks')
		time.sleep(1.0)

def KeyboardSupport():
	while True:
		report = get_key()
		# print(report)
		if report:
			for event in report:
				print("-------")
				print(event.ev_type, event.code, event.state)
				print("-------")
				match event.code:
					case "BTN_THUMBL":
						SetEnableAll(0)
						print("L3 pressed")
					case "BTN_THUMBR":
						SetEnableAll(1)
						print("R3 pressed")
					case "ABS_X":
						if controller_type == "PS4":
							if event.state == 0:
								left_joy_H = event.state / MAX_JOY_VAL
						else:
							left_joy_H = event.state / MAX_JOY_VAL
					case "ABS_Y":
						left_joy_V = event.state / MAX_JOY_VAL
					case "ABS_RX":
						right_joy_H = event.state / MAX_JOY_VAL
					case "ABS_RY":
						right_joy_V = event.state / MAX_JOY_VAL
					case "BTN_START":
						SetEnableAll(1)
						print("Start pressed")
					case "ABS_LZ":
						SetEnableAll(0)
						print("L3 pressed")


				P1 = (2.0/3.0)*left_joy_H+(1.0/3.0)*right_joy_H
				P2 = (-1.0/3.0)*left_joy_H+(1.0/math.sqrt(3.0))*left_joy_V+(1.0/3.0)*right_joy_H
				P3 = (-1.0/3.0)*left_joy_H-(1.0/math.sqrt(3.0))*left_joy_V+(1.0/3.0)*right_joy_H

				# # Motors are reversed
				P1 = -round(P1,3)
				P2 = -round(P2,3)
				P3 = -round(P3,3)

				print("=======")
				print("P1:", P1)
				print("P2:", P2)
				print("P3:", P3)
				print("=======")

				if( abs(P1 ) < 0.1 ) :  P1 = 0
				if( abs(P2 ) < 0.1 ) :  P2 = 0
				if( abs(P3 ) < 0.1 ) :  P3 = 0

				if( abs( P1 - last_P1 ) > 0.05 ):
							last_P1 = P1
							cmd = "set M0 " + str(P1)
							ser.write((cmd + '\n').encode())
					#while ser.in_waiting > 0:
							#response = ser.readline().decode('utf-8').rstrip()
							#print(f"ESP32 Response: {response}")

				if( abs( P2 - last_P2 ) > 0.05 ):
							last_P2 = P2
							cmd = "set M1 " + str(P2)
							ser.write((cmd + '\n').encode())
					#while ser.in_waiting > 0:
							#response = ser.readline().decode('utf-8').rstrip()
							#print(f"ESP32 Response: {response}")

				if( abs( P3 - last_P3 ) > 0.05 ):
							last_P3 = P3
							cmd = "set M3 " + str(P3)
							ser.write((cmd + '\n').encode())
					#while ser.in_waiting > 0:
							#response = ser.readline().decode('utf-8').rstrip()
							#print(f"ESP32 Response: {response}")

				print("left_joy_H", left_joy_H)
				print("left_joy_V", left_joy_V)
				print("right_joy_H", right_joy_H)
				print("right_joy_V", right_joy_V)
				print("=================")
		else:
			#state = None
			time.sleep(0.1)
			#print('Unable to get controller state')


if __name__ == "__main__":
	DetermineInput()
