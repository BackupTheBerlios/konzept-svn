# -*- coding: UTF-8 -*-

class MemorySource:
	""" Allow using the main memory as data source.
	    Looks dirty hacked, I know! But the the Python I/O model
	    is anyway a big dirty hack.
	"""
	def __init__(self, buf):
		self._buf = buf

	def read(self, bufSize = None):
		return self._buf
