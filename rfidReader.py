#!/usr/bin/env python3.2
import ctypes
import os
import binascii
import threading
import time
import queue

class nfc_iso14443a_info(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("abtAtqa", ctypes.c_ubyte*2), ("btSak", ctypes.c_ubyte), ("szUidLen", ctypes.c_size_t), ("abtUid", ctypes.c_ubyte*10), ("szAtsLen", ctypes.c_size_t), ("abtAts", ctypes.c_ubyte*254)]

class nfc_target_info(ctypes.Union):
	_fields_ = [("nai", nfc_iso14443a_info)]

class nfc_modulation(ctypes.Structure):
	_fields_ = [("nmt", ctypes.c_int), ("nbr", ctypes.c_int)]

class nfc_target(ctypes.Structure):
	_fields_ = [("nti", nfc_target_info), ("nm", nfc_modulation)]

class rfidReaderThread(threading.Thread):
	def __init__(self, messageQueue):
		threading.Thread.__init__(self)
		self._exit = False
		self._queue = messageQueue

	def stop(self):
		self._exit = True

	def run(self):
		self.nfc = ctypes.cdll.LoadLibrary(os.path.dirname(__file__)+"/libnfchelper.so")
		self.device = self.nfc.openDevice()
		self.nfc.nfc_initiator_init(self.device)
		self.nt = nfc_target()
		while not self._exit:
			nmModulations = nfc_modulation()
			nmModulations.nmt = 1
			nmModulations.nbr = 1
			res = self.nfc.nfc_initiator_poll_target(self.device, ctypes.byref(nmModulations), 1, 1, 2, ctypes.byref(self.nt))
			if res > 0:
				print("----------------------")
				uid = bytes(self.nt.nti.nai.abtUid[:self.nt.nti.nai.szUidLen])
				print(uid)
				print(binascii.hexlify(uid).decode('ascii'))
				self._queue.put(uid)
				#Kurz warten, um Mehrfacherkennungen zu reduzieren
				time.sleep(2)
				while (self.nfc.nfc_initiator_target_is_present(self.device, None) == 0) and not self._exit:
					pass

if __name__ == '__main__':
	t = rfidReaderThread()
	t.start()
	time.sleep(10)
	t.stop()
	t.join()
