# -*- coding: UTF-8 -*-

from xmlfactory import *
from xmltokensource import *

class List:
	def __init__(self, id = None, elementType = None):
		self._id = id
		self._elementType = elementType
		self._l = []
	
	def id(self): return self._id
	
	def staticTypeName(): return "List"
	def typeName(self): return List.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(args = None):
		if args == None:    
			return List()
		else:
			return List(args[0], args[1])
	newInstance = staticmethod(newInstance)

	def append(self, e): self._l.append(e)
	def __iter__(self): return self._l.__iter__()
	def __getitem__(self, i): return self._l[i]
	def __setitem__(self, i, x): self._l[i] = x
	
	def push(self, e): self._l.append(e)
	def pop(self, i = -1): return self._l.pop(i)
	
	def top(self): return self._l[0]
	def head(self): return self._l[0]
	def tail(self): return self._l[-1]
	def count(self): return len(self._l)
	def removeAll(self): self._l = []
	
	def copy(self):
		l2 = List()
		for e in self._l:
			l2.append(e)
		return l2

	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		sink.stepDown()
		if self.id() != None:
			sink.write("<id>%s</id>\n" % self.id())
		for e in self:
			e.writeXml(sink)
		sink.stepUp()
		sink.write("</%s>\n" % self.typeName())

	def readXml(self, source, path):
		path.append(self)
		self.removeAll()
		source.get("<%s>" % self.typeName())
		if source.lookAhead() == tag("<id>"):
			source.get("<id>")
			self._id = source.get().value()
			source.get("</id>")
		while source.lookAhead() != tag("</%s>" % self.typeName()):
			element = XmlFactory.instance(self._elementType).createFromXml(source, path)
			self.append(element)
		source.get("</%s>" % self.typeName())
		path.pop()

XmlFactory.instance(List).registerType(List)
