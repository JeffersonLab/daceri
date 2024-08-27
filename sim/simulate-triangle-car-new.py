import time
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import mujoco
import mujoco.viewer
import math
import glfw

from approxeng.input.selectbinder import ControllerResource

paused = False

def key_callback(keycode):
  if chr(keycode) == ' ':
    paused = not paused

m = mujoco.MjModel.from_xml_path('xml-triangle-car.xml')
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
				acc_matrix.append(np.mean(d.qacc))
				step_start = time.time()
				print("Current time:", time.time() - start)
				time_matrix.append(time.time() - start)

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
	matplotlib.use("TkAgg")
	plt.plot(time_matrix, pos_matrix, label='time vs. position')
	plt.grid(True)
	plt.xlabel("time (seconds)")
	plt.ylabel("position (meters)")
	#plt.plot(time_matrix, vel_matrix, label='time vs. velocity')
	plt.legend()
	plt.show()
