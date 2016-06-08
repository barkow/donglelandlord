#!/usr/bin/python3
import json
import urllib.request
import ssl
import base64
import logging
import configparser

configfile = "usbDongleLandlord.conf"

config = configparser.ConfigParser()
config.read(configfile)

class jiraDongle():
	def __init__(self, jiraId):
		self.jiraId = jiraId
		self._jiraTransitIdRemove = 71
		self._jiraTransitIdReturn = 81
		self._jiraUser = config['JIRA']['apiuser']
		self._jiraPassword = config['JIRA']['apipassword']
		self._jiraUrl = config['JIRA']['apiurl']

	def getStatus(self):
		req = urllib.request.Request(url=self._jiraUrl+'issue/{}?fields=status'.format(self.jiraId), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		return data['fields']['status']['name']

	def getUsbAddress(self):
		req = urllib.request.Request(url=self._jiraUrl+'issue/{}?fields=description'.format(self.jiraId), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		return data['fields']['description'].replace("USBADDRESS:","")

	def _sendTransitionRequest(self, transitionId):
		try:
			req = urllib.request.Request(url=self._jiraUrl+'issue/{}/transitions'.format(self.jiraId),  data = json.dumps({'transition': {'id': "{}".format(transitionId)}}).encode(), headers={"Content-Type":"application/json"})
			userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
			req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
			resp =  urllib.request.urlopen(req)
			body = resp.read()
		except:
			logging.error("Error changing Dongle {} with tranistion {}".format(self.jiraId, transitionId))

	def remove(self):
		self._sendTransitionRequest(self._jiraTransitIdRemove)

	def retu(self):
		self._sendTransitionRequest(self._jiraTransitIdReturn)

class jiraServer():
	def __init__(self):
		self._jiraUser = config['JIRA']['apiuser']
		self._jiraPassword = config['JIRA']['apipassword']
		self._jiraUrl = config['JIRA']['apiurl']

	def getAllDongles(self):
		req = urllib.request.Request(url=self._jiraUrl+'search',  data = json.dumps({'jql': "project = USBDONGLE", 'fields': ["key"]}).encode(), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		
		dongles = []
		for dongle in data['issues']:
			dongles.append(jiraDongle(dongle['key']))
		return dongles

	def getConnectedDongles(self):
		req = urllib.request.Request(url=self._jiraUrl+'search',  data = json.dumps({'jql': "project = USBDONGLE AND status = Connected", 'fields': ["key"]}).encode(), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		
		dongles = []
		for dongle in data['issues']:
			dongles.append(jiraDongle(dongle['key']))
		return dongles

	def GetRemovedDongles(self):
		pass

	def GetBorrowedDongles(self):
		pass

	def getDongle(self, usbAddress):
		req = urllib.request.Request(url=self._jiraUrl+'search',  data = json.dumps({'jql': "project = USBDONGLE AND description ~ USBADDRESS:{}".format(usbAddress), 'fields': ["key"]}).encode(), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		if data['total'] == 1:
			return jiraDongle(data['issues'][0]['key'])
		else:
			return None


#klappt unter python 3.2 nicht
#passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
#passman.add_password(realm=None, uri=self._jiraUrl+"issue/USBDONGLE-1/transitions", user='s', passwd='ppp')
#auth_handler = urllib.request.HTTPBasicAuthHandler(passman)
#opener = urllib.request.build_opener(auth_handler)
#urllib.request.install_opener(opener)

#req = urllib.request.Request(url=self._jiraUrl+'issue/USBDONGLE-1/transitions',  headers={"Content-Type":"application/json"})
#userAndPass = base64.b64encode("{}:{}".format(self._jiraUser, self._jiraPassword).encode()).decode("ascii")
#headers = { 'Authorization' : 'Basic %s' %  userAndPass }
#req.add_header("Authorization", 'Basic %s' %  userAndPass)   
#resp =  urllib.request.urlopen(req)
#pprint.pprint(resp.read())


if __name__ == '__main__':
	s = jiraServer()
	ds = s.getAllDongles()
	logging.debug("OK")
