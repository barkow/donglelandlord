#!/usr/bin/env python3.2
import rfidReader
import threading
import urllib.request
import json
import base64
import binascii
import html.parser
import time
import queue
import binascii
import logging
import configparser

configfile = "usbDongleLandlord.conf"

config = configparser.ConfigParser()
config.read(configfile)

class ifaicMitarbeiterlisteKompaktParser(html.parser.HTMLParser):
		def __init__(self, personalnummer):
			self.activeRow = False
			self.personalnummer = personalnummer
			self.personFound = False
			self.surname = None
			self.givenName = None
			self.userName = None
			self.columnCounter = 0
			super().__init__(strict=False)

		def handle_starttag(self, tag, attrs):
			if tag == "tr":
				self.activeRow = True

			if self.activeRow:
				if tag == "a":
					if self.personalnummer in attrs[1][1]:
						self.personFound = True
			if self.personFound:
				if tag == "td":
					self.columnCounter = self.columnCounter + 1
					

		def handle_endtag(self, tag):
			if tag == "tr":
				self.activeRow = False
				self.personFound = False

		def handle_data(self, data):
			if self.personFound:
				if self.columnCounter == 0:
					self.surname = data

				if self.columnCounter == 1:
					self.givenName = data

class ifaicMitarbeiterlisteParser(html.parser.HTMLParser):
		def __init__(self, personalnummer):
			self.activeRow = False
			self.personalnummer = personalnummer
			self.personFound = False
			self.surname = None
			self.givenName = None
			self.columnCounter = 0
			super().__init__(strict=False)

		def handle_starttag(self, tag, attrs):
			if tag == "tr":
				self.activeRow = True

			if self.activeRow:
				if tag == "a":
					if self.personalnummer in attrs[1][1]:
						self.personFound = True
			if self.personFound:
				if tag == "td":
					self.columnCounter = self.columnCounter + 1
					

		def handle_endtag(self, tag):
			if tag == "tr":
				self.activeRow = False
				self.personFound = False

		def handle_data(self, data):
			if self.personFound:
				if self.columnCounter == 0:
					self.surname = data

				if self.columnCounter == 1:
					self.givenName = data

				if self.columnCounter == 7:
					(user, domain) = data.split('@')
					self.userName = user
					raise Exception()


class rfidIdentifierThread(threading.Thread):
	def __init__(self, newUserAction = None, newUserElapsedAction = None):
		threading.Thread.__init__(self)
		self._exit = False
		self._rfidReaderQueue = queue.Queue()
		self.rfidReader = rfidReader.rfidReaderThread(self._rfidReaderQueue)
		self._url = config['IFAIC']['apiurl']
		self._user = config['IFAIC']['apiuser']
		self._password = config['IFAIC']['apipassword']
		self._mitarbeiterlisteUrl = config['IFAIC']['mitarbeiterlisteurl']

		self._activeUser = None
		self._activeUserActivation = 0
		self._activeUserSemaphore = threading.Semaphore()
		self._activeUserActivationPeriod = 5

		self._newUserAction = newUserAction
		self._newUserElapsedAction = newUserElapsedAction

	def _setActiveUser(self, user):
		logging.debug("SetActiveUser")
		with self._activeUserSemaphore:
			self._activeUser = user
			self._activeUserActivation = time.time()
		if self._newUserAction:
			logging.debug("Start newUserAction")
			self._newUserAction()


	def getActiveUser(self):
		logging.debug("GetActiveUser")
		with self._activeUserSemaphore:
			retVal = (self._activeUser, self._activeUserActivation)
		return retVal

	def stop(self):
		self._exit = True

	def run(self):
		self.rfidReader.start()
		while not self._exit:
			try:
				uid = self._rfidReaderQueue.get(block=True, timeout=1)
				logging.debug("rfidIdentifierThread")
				logging.debug(uid)
				user = self.getCardDetails(uid)
				logging.debug(user)
				self._setActiveUser(user)
				logging.debug("user set")
				self._rfidReaderQueue.task_done()
			except:
				#Prüfen ob der aktive User zurückgesetzt werden muss
				if self._activeUser:
					if time.time() - self._activeUserActivation >= self._activeUserActivationPeriod:
						self._activeUser = None
						if self._newUserElapsedAction:
							logging.debug("Start newUserElapsedAction")
							self._newUserElapsedAction()
				
		self.rfidReader.stop()
		self.rfidReader.join()

	def getCardDetails(self, uid):
		#StaffId von ifaic mittels UID der Karte abfragen
		logging.debug("request ifaic staff id")
		req = urllib.request.Request(url=self._url+'cards/{}'.format(binascii.hexlify(uid).decode('ascii')), headers={"Content-Type":"application/json"})
		userAndPass = base64.b64encode("{}:{}".format(self._user, self._password).encode()).decode("ascii")
		req.add_header("Authorization", 'Basic {:s}'.format(userAndPass))
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		data = json.loads(body.decode())
		staffId = data['ikaFkaIdentStaffId']
		
		#Aus StaffId und ifaic Mitarbeiterseite Vorname und Nachname herausfinden
		#req = urllib.request.Request(url='https://ifaic.ika.rwth-aachen.de/info/mitarbeiterliste_komp.php')
		logging.debug("request ifaic user name")
		req = urllib.request.Request(url=self._mitarbeiterlisteUrl)
		resp =  urllib.request.urlopen(req)
		body = resp.read()
		logging.debug("parse response")
		#Für schnelleres Parsen wird beim finden eines Ergebnis eine Exception geworfen
		try:
			parser = ifaicMitarbeiterlisteParser(staffId)
			parser.feed(body.decode('iso-8859-1'))
		except:
			logging.debug("parsed")
			logging.debug(parser.userName)
			return parser.userName
		return None

if __name__ == '__main__':
	def userElapsedAction():
		logging.debug("This is my user elapsed action")

	logging.basicConfig(level=logging.DEBUG)
	logging.debug("Launch Test Program")
	r = rfidIdentifierThread(newUserElapsedAction = userElapsedAction)
	r.start()
	for i in (1,2,3):
		user = r.getActiveUser()
		print(user)
		time.sleep(15)
	print("stop 1")
	r.stop()
	print("wait stop 1")
	r.join()
