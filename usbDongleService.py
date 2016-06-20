#!/usr/bin/python3.2
import pyudev
import pprint
import time
import jiraInterface
import os.path
import rfidIdentifier
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

context = pyudev.Context()
s = jiraInterface.jiraServer()

monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

rfid = rfidIdentifier.rfidIdentifierThread()
rfid.start()

def device_event(device):
	#print("EVENT")
	logging.debug('background event {0.action}: {0.device_path}'.format(device))
	(head, tail) = os.path.split(device['DEVPATH'])
	try:
		d = s.getDongle(tail)
		if not d:
			logging.warning("Couldn't find dongle in jira: {0.device_path}".format(device))
			logging.debug("Search for {}".format(tail))
			return

		if device.action == 'add':
			d.retu()

		if device.action == 'remove':
			user = rfid.getActiveUser()
			logging.debug(user)
			logging.debug(user[0])
			if user[0]:
				logging.info("User {} authenticated, borrowing dongle {}".format(user[0], device.device_path))
			else:
				logging.info("No user authenticated, removing dongle {0.device_path}".format(device))
				d.remove()
	except:
		logging.warning("Couldn't do action on dongle {0.device_path}".format(device))
		logging.debug(sys.exc_info()[0])
		logging.debug(sys.exc_info()[1])

#observer = pyudev.MonitorObserver(monitor, callback=device_event, name='monitor-observer')
#observer.start()
#c = input("Eingabe.")

while 1:
	device = monitor.poll(timeout=3)
	if device:
		device_event(device)

rfid.stop()
rfid.join()
			
