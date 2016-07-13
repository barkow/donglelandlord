#!/usr/bin/env python3.2
import ctypes
import os
import binascii
import threading
import time
import queue
import logging

class nfc_iso14443a_info(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("abtAtqa", ctypes.c_ubyte*2), ("btSak", ctypes.c_ubyte), ("szUidLen", ctypes.c_size_t), ("abtUid", ctypes.c_ubyte*10), ("szAtsLen", ctypes.c_size_t), ("abtAts", ctypes.c_ubyte*254)]

class nfc_target_info(ctypes.Union):
	_fields_ = [("nai", nfc_iso14443a_info)]

class nfc_modulation(ctypes.Structure):
	_fields_ = [("nmt", ctypes.c_int), ("nbr", ctypes.c_int)]

class nfc_target(ctypes.Structure):
	_fields_ = [("nti", nfc_target_info), ("nm", nfc_modulation)]


class nfc_user_defined_device(ctypes.Structure):
	_fields_ = [("name", ctypes.c_char*256), ("connstring", ctypes.c_char*1024), ("optional", ctypes.c_bool)]

class nfc_context(ctypes.Structure):
	_fields_ = [("allow_autoscan", ctypes.c_bool),("allow_intrusive_scan",ctypes.c_bool ),("log_level", ctypes.c_ulong),("user_defined_devices", nfc_user_defined_device*4),("user_defined_device_count", ctypes.c_uint)]

#Aus pn53x-internal.h
PN53X_SFR_P3 = 0xFFB0
P32 = 2
P33 = 3
PN53X_SFR_P7CFGA = 0xFFF4
PN53X_SFR_P7CFGB = 0xFFF5
PN53X_SFR_P7 = 0xFFF7

class rfidReaderThread(threading.Thread):
	def __init__(self, messageQueue):
		threading.Thread.__init__(self)
		self._exit = False
		self._queue = messageQueue

	def stop(self):
		self._exit = True

	def _openDevice(self):
		context = ctypes.POINTER(nfc_context)()
		self.nfc.nfc_init(ctypes.byref(context))
		if not context:
			raise Exception()
		devices = ((ctypes.c_char*1024)*8)()
		device_count = self.nfc.nfc_list_devices(context, devices, 8)
		if device_count <= 0:
			raise Exception()
		for i in range(device_count):
			self.device = self.nfc.nfc_open(context, devices[i])
			if self.device:
				break
		if not self.device:
			raise Exception()

		self._initGpio71()

	def _initGpio71(self):
		#GPIO71 (MISO) als Ausgang konfigurieren
		self.nfc.pn53x_write_register(self.device, PN53X_SFR_P7CFGB, 1 << 1, 0xff)


	def setGpio71(self):
		self.nfc.pn53x_write_register(self.device, PN53X_SFR_P7, 1 << 1, 0xff)

	def clearGpio71(self):
		self.nfc.pn53x_write_register(self.device, PN53X_SFR_P7, 1 << 1, 0x00)

	def run(self):
		self.nfc = ctypes.cdll.LoadLibrary("libnfc.so")
		self._openDevice()
		self.nfc.nfc_initiator_init(self.device)
		self.nt = nfc_target()
		while not self._exit:
			nmModulations = nfc_modulation()
			nmModulations.nmt = 1
			nmModulations.nbr = 1
			res = self.nfc.nfc_initiator_poll_target(self.device, ctypes.byref(nmModulations), 1, 1, 2, ctypes.byref(self.nt))
			if res > 0:
				logging.debug("----------------------")
				uid = bytes(self.nt.nti.nai.abtUid[:self.nt.nti.nai.szUidLen])
				logging.debug(uid)
				logging.debug(binascii.hexlify(uid).decode('ascii'))
				self._queue.put(uid)
				#Kurz warten, um Mehrfacherkennungen zu reduzieren
				time.sleep(2)
				while (self.nfc.nfc_initiator_target_is_present(self.device, None) == 0) and not self._exit:
					pass

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	logging.debug("Launch Test Program")
	q = queue.Queue()
	t = rfidReaderThread(q)
	t.start()
	time.sleep(10)
	t.stop()
	t.join()
