import pyudev
import pprint
import os.path
import jiraInterface

context = pyudev.Context()

s = jiraInterface.jiraServer()


#Schleife ueber alle angeschlossenen Dongle
#deren Adresse wird gemerkt
dongleAddresses = []
for device in context.list_devices(subsystem='usb'):
	#Nur einzelne USB Devices beruecksichtigen
	if device['DEVTYPE'] == "usb_device":
		(head, tail) = os.path.split(device['DEVPATH'])
		dongleAddresses.append(tail)

dongles = s.getAllDongles()
for dongle in dongles:
	status = dongle.getStatus()
	usbAddress = dongle.getUsbAddress()
	if usbAddress in dongleAddresses:
		if status != "Connected":
			print("set dongle connected")
			dongle.retu()
	else:
		if status == "Connected":
			print("set dongle removed")
			dongle.remove()