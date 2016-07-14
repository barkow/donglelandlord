#!/usr/bin/python3.2
import pprint
import os.path
import jiraInterface
import getpass

config = {}
config['JIRA'] = {}
config['JIRA']['apiuser'] = getpass.getpass("Jira-User: ")
config['JIRA']['apipassword'] = getpass.getpass() 
config['JIRA']['apiurl'] = "https://jira.ika.rwth-aachen.de/rest/api/2/"
jiraInterface.init(config)
s = jiraInterface.jiraServer()


dongles = s.getAllDongles()
descriptionString = ""
for dongle in dongles:
	status = dongle.getStatus()
	usbAddress = dongle.getUsbAddress()
	vid = dongle.getUsbVid()
	pid = dongle.getUsbPid()
	desc = dongle.getDescription()
	descriptionStringPart = "{3},{1},{2},{0}".format(usbAddress.replace("-","").replace(".",""), vid, pid, desc)
	print(descriptionStringPart)
	descriptionString = descriptionString + descriptionStringPart + ","

print("DeviceNicknames={}".format(descriptionString).strip(","))
