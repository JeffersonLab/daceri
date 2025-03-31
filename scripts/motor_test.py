#from REVHubInterface import REVcomm 


#commMod.listPorts()

#from REVHubInterface import REVModule
# module = REVModule.Module(commMod)
# print(module.getStatus)

# Get I2C channel devices:
# REVModules[module_number].i2cChannels[bus_number].getDevices()
# REVModules[module_number].i2cChannels[0].addIMU(str(module_number) + 'IMU')
# REVModules[module_number].i2cChannels[0].getDevices()[str(module_number) + 'IMU'].initSensor()

from REVHubInterface import REVcomm 
from REVHubInterface import REVModule
import time

try: 
	
	commMod = REVcomm.REVcomm()
	commMod.openActivePort()
	REVModules = []
	REVModules = commMod.discovery()
	moduleNames = []
	for i in range(0, len(REVModules)):
		moduleNames.append('REV Expansion Hub ' + str(i))
	moduleTot=len(moduleNames)

	print(moduleTot)
	
	motor_num = 0
	REVModules[0].motors[motor_num].setMode(0,1)
	REVModules[0].motors[motor_num].enable()
	REVModules[0].motors[motor_num].setPower(float(0.5*32000))
	time.sleep(3)
	REVModules[0].motors[motor_num].disable()
	#REVModules[0].motors[motor_num].setPower(float(0))
	
	REVModules[0].i2cChannels[0].getDevices()
	REVModules[0].i2cChannels[0].addIMU(str(0) + 'IMU')
	REVModules[0].i2cChannels[0].getDevices()[str(0) + 'IMU'].initSensor()
	
except Exception as e:
	print(e)
	print("Error Searcing for Hubs")

# try: 
	# REVModules = []
	# REVModules = commMod.discovery()
	# moduleTot = len(checkForModules())
	# # self.repetitiveFunctions.append((lambda: self.send_all_KA()))
	# moduleNames = []
	# for i in range(0, len(self.REVModules)):
		# moduleNames.append('REV Expansion Hub ' + str(i))
	# print(moduleNames)
# except Exception as e:
	# print("error")
