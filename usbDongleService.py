#!/usr/bin/python3.2
import pyudev
import pprint
import time
import jiraInterface
import os.path

context = pyudev.Context()
s = jiraInterface.jiraServer()

monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')
def device_event(device):
	#print("EVENT")
	#print('background event {0.action}: {0.device_path}'.format(device))
	(head, tail) = os.path.split(device['DEVPATH'])
	d = s.getDongle(tail)
	if device.action == 'add':
		d.retu()

	if device.action == 'remove':
		d.remove()

#observer = pyudev.MonitorObserver(monitor, callback=device_event, name='monitor-observer')
#observer.start()
#c = input("Eingabe.")
while 1:
	device = monitor.poll(timeout=3)
	if device:
		device_event(device)
