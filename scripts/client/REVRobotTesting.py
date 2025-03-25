import REVHubInterface

from REVHubInterface import REVMotor
from REVHubInterface import REVcomm

# motor = REVMotor() # Motor.__init__() missing 3 required positional arguments: 'commObj', 'channel', and 'destinationModule'

commMod = REVcomm()

allPorts = self.commMod.listPorts()

# allPorts should let us know where REVHub is at
if len(allPorts) == 0:
	errMsg = 'No available com ports, verify connection and try again.\n'
	tkinter.messagebox.showinfo('Invalid Firmware', errMsg)
	self.firmware.warning_block.insert(END, errMsg)
else:
	port = allPorts[0].getNumber()

# Check modules
self.commMod.openActivePort()
moduleTot = len(self.checkForModules())

# for moduleNumber in range(0, moduleTot):
	# for motorNumber in range(0, 4):
                # self.Motor_packs[-1].Motor_pack.config(text='Module: ' + str(moduleNumber) + ' Motors: ' + str(motorNumber))

# self.REVModules[moduleNumber].motors[motorNumber].setMode(0, 1)
# self.REVModules[moduleNumber].motors[motorNumber].setPower(float(speed))
# self.REVModules[moduleNumber].motors[motorNumber].enable()
