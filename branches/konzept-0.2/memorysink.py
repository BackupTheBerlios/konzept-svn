# -*- coding: UTF-8 -*-

class MemorySink:
	""" Allow using the main memory as data sink. """
	def __init__(self):
		self._buf = ""
	def write(self, v):
		self._buf += v
	def buf(self):
		return self._buf