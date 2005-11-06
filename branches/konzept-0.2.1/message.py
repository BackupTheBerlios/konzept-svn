# -*- coding: UTF-8 -*-

from xmlfactory import *
from map import *
from atomics import *
from xmltokensource import *
from indentsink import *
from memorysink import *
from memorysource import *

class Message(Map):
	""" Advances the Map to make it applyable for implementing
	    message based protocols over TCP/UDP using XML serialization. """

	def __init__(self):
		Map.__init__(self)
		
	def staticTypeName(): return "Message"
	def typeName(self): return Message.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return Message()
	newInstance = staticmethod(newInstance)

	# == reading / writing message from XML string
	
	def toXml(self):
		mem = MemorySink()
		self.writeXml(IndentSink(mem))
		return mem.buf()
		
	def fromXml(self, s):
		self.readXml(XmlTokenSource(s), [])

	# == reading / writing message from XML string with leading length code
	
	def writeFrame(self, sink):
		xml = self.toXml()
		lc = "%08X\n" % len(xml)
		sink.send(lc + xml)                 # handling for EINTR??!
		
	def readFrame(self, source):
		lc = source.recv(8+len("\n"))
		if len(lc) != 8+len("\n"): return 0
		lc = int(lc, 16)
		xml = ""
		print "Message.readFrame(): lc =", lc
		while lc > 0:
			s = source.recv(lc)
			lc -= len(s)
			xml = xml + s
		print "Message.readFrame(): xml =", xml
		print "Message.readFrame(): len(xml) =", len(xml)
		self.fromXml(xml)
		return 1
		
	def writeXmlFrame(self, sink): self.writeFrame(sink)
	def readXmlFrame(self, source): self.readFrame(source)
	
XmlFactory.instance(Message).registerType(Message)
