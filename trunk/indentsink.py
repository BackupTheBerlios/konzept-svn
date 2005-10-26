# -*- coding: UTF-8 -*-

from re import *

def relaceXmlSymbols(s):
	s = sub("&", "&amp;", s)
	s = sub("<", "&lt;", s)
	s = sub(">", "&gt;", s)
	return s

class IndentSink:
	""" Inherit "XmlSink" with writeNumber(), writeString() 
	    and automatic special character replacement and
	    automatic stepUp() and stepDown()
	    e.g.:
	    open(typeName())
	    putInt()
	    putStr()
	    putFloat()
	    close(typeName())
	    => Anlehnung an Xstream
	"""

	def __init__(self, sink):
		self._sink = sink
		self._depth = 0
		self._prefix = ""

	def depth(self): return self._depth

	def stepDown(self):
		self._depth = self._depth + 1
		self._prefix = self._prefix + '\t'

	def stepUp(self):
		if self._depth == 0: return
		self._depth = self._depth - 1
		self._prefix = self._prefix[0:len(self._prefix)-1]

	def setDepth(self, depth):
		self._depth = depth
		self._prefix = ""
		for i in range(depth):
			self._prefix = self._prefix + "\t"

	def write(self, s):
		self._sink.write(self._prefix + s)
