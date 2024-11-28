import time
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import gridspec
import numpy as np
import mujoco
import mujoco.viewer
import math
import glfw
import sys

from approxeng.input.selectbinder import ControllerResource

paused = False

def key_callback(keycode):
  if chr(keycode) == ' ':
    paused = not paused

if len(sys.argv) > 1:
	xml_path = sys.argv[1]
m = mujoco.MjModel.from_xml_path(xml_path)
d = mujoco.MjData(m)
#b = mujoco.MjsBody(m)

with mujoco.viewer.launch_passive(m, d, key_callback=key_callback) as viewer:
	# Close the viewer automatically after X wall-seconds.
	start = time.time()
	pos_matrix = []
	vel_matrix = []
	acc_matrix = []
	time_matrix = []
	limit = 500
	time_limit = 120
	# Set an initial velocity for a joint (e.g., assuming joint index 0)
	initial_velocity = 5  # set your desired initial velocity
	print(m.actuator_user)
	#qpos[1] shows the position of the robot baseplate
	try:
		with ControllerResource() as joystick:
			while viewer.is_running() and joystick.connected and time.time() - start < time_limit:
				print('pos (x):', np.mean(d.xpos))
				pos_matrix.append(np.mean(d.xpos))
				print('vel:', np.mean(d.qvel))
				vel_matrix.append(np.mean(d.qvel))
				print('accel:', np.mean(d.qacc))
				acc_matrix.append(np.mean(d.qacc))
				step_start = time.time()
				print("Current time:", time.time() - start)
				time_matrix.append(time.time() - start)
				print("*==*")

				presses = joystick.check_presses()
				lx, ly = joystick['l']
				rx, ry = joystick['r']
				ls = joystick['ls']
				rs = joystick['rs']
				a = joystick['cross']
				x = joystick['square']
				c = joystick['circle']

				P1 = (-1)*lx+(1.0/3.0)*rx
				P2 = (1.0/2.0)*lx+(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
				P3 = (1.0/2.0)*lx-(math.sqrt(3.0)/2)*ly+(1.0/3.0)*rx
				d.ctrl[0] = limit*P1
				d.ctrl[1] = limit*P2
				d.ctrl[2] = limit*P3

				#if time.time() - start > 119.999:
				#mujoco.mj_resetData(m, d)


				# mj_step can be replaced with code that also evaluates
				# a policy and applies a control signal before stepping the physics.
				mujoco.mj_step(m, d)

				# Example modification of a viewer option: toggle contact points every two seconds.
				with viewer.lock():
					viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

					# Pick up changes to the physics state, apply perturbations, update options from GUI.
				viewer.sync()

					# Rudimentary time keeping, will drift relative to wall clock.
				time_until_next_step = m.opt.timestep - (time.time() - step_start)
				if time_until_next_step > 0:
					time.sleep(time_until_next_step)

	except IOError:
		# No joystick found, wait for a bit before trying again
		print('Unable to find any joysticks')
		time.sleep(1.0)

	print("Total number of degrees of freedom", m.nv)
	mujoco.mj_printData(m, d, 'test_data')
	matplotlib.use("TkAgg")
#	plt.plot(time_matrix, pos_matrix, label='time vs. position')
#	plt.grid(True)
#	plt.xlabel("time (seconds)")
#	plt.ylabel("position (meters)")
#	#plt.plot(time_matrix, vel_matrix, label='time vs. velocity')
#	plt.legend()
#	plt.show()

	fig1=plt.figure(1)

	gs = gridspec.GridSpec(2, 2)



	ax0 = plt.subplot(gs[0])
	ax1 = plt.subplot(gs[1], sharex=ax0)
	ax2 = plt.subplot(gs[2], sharex=ax0)


	ax0.set_title("Time vs. Pos")
	ax1.set_title("Time vs. Vel")
	ax2.set_title("Time vs. Acc")

	ax0.set_ylabel('Position (m)', fontsize=12)
	ax1.set_ylabel('Velocity (m/s)', fontsize=12)
	ax2.set_ylabel('Acceleration (m/s^2)', fontsize=12)

	xlabel = "Time (seconds)"
	title = "Mujoco Simulation Measurements (Collapsed Elevator)"
	fig1.supxlabel(xlabel, fontsize=14) # Add the x-axis label, "fontsize" is optional
	fig1.suptitle(title, fontsize=14)

	line0, = ax0.plot(time_matrix, pos_matrix, color='r', linestyle='--')
	line1, = ax1.plot(time_matrix, vel_matrix, color='b', linestyle='-.')
	line2, = ax2.plot(time_matrix, acc_matrix, color='g', linestyle=':')

#	ax2.legend((line0, line1, line2), ('Time vs. Pos', 'Time vs. Vel','Time vs. Acc'), loc='upper left', fontsize=10)

	ax0.plot(time_matrix, pos_matrix, color='r', linestyle='--')
	ax1.plot(time_matrix, vel_matrix, color='b', linestyle='-.')
	ax2.plot(time_matrix, acc_matrix, color='g', linestyle=':')

	ax0.grid(True)
	ax1.grid(True)
	ax2.grid(True)

	#plt.tight_layout(pad=0.1, w_pad=0.1, h_pad=.5)
	# remove vertical gap between subplots
	plt.subplots_adjust(wspace=.35)
	plt.subplots_adjust(hspace=.3)
	plt.show()

	# Plot the data on a new figure
	fig1.show()
