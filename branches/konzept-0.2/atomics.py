# -*- coding: UTF-8 -*-

from xmlfactory import *

def isAtomic(x): return type(x) in [int, float, str]

class Atomic:
	def __init__(self, x = None):
		self._x = x

	def __hash__(self): return self._x.__hash__()
	def __cmp__(self, b): return self.__hash__() - b.__hash__()
	
	def value(self): return self._x
	def setValue(self, x): self._x = x

class Int(Atomic):
	def __init__(self, x = None):
		Atomic.__init__(self, x)
	
	def staticTypeName(): return "Int"
	def typeName(self): return Int.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return Int()
	newInstance = staticmethod(newInstance)
	
	def writeXml(self, sink):
		sink.write("<Int>%d</Int>\n" % self._x)
	
	def readXml(self, source, path):
		path.append(self)
		source.get("<Int>")
		self._x = int(source.get().value())
		source.get("</Int>")
		path.pop()

XmlFactory.instance(Atomic).registerType(Int)
XmlFactory.instance(Int).registerType(Int)

class Float(Atomic):
	def __init__(self, x = None):
		Atomic.__init__(self, x)
	
	def staticTypeName(): return "Float"
	def typeName(self): return Float.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return Float()
	newInstance = staticmethod(newInstance)
	
	def writeXml(self, sink):
		sink.write("<Float>%f</Float>\n" % self._x)
	
	def readXml(self, source, path):
		path.append(self)
		source.get("<Float>")
		self._x = float(source.get().value())
		source.get("</Float>")
		path.pop()

XmlFactory.instance(Atomic).registerType(Float)
XmlFactory.instance(Float).registerType(Float)

class Str(Atomic):
	def __init__(self, x = None):
		Atomic.__init__(self, x)
	
	def staticTypeName(): return "Str"
	def typeName(self): return Str.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return Str()
	newInstance = staticmethod(newInstance)
	
	def __hash__(self): return self._x.__hash__()
	def __cmp__(self, b): return self.__hash__() - b.__hash__()
	
	def writeXml(self, sink):
		sink.write("<Str>%s</Str>\n" % self._x)
	
	def readXml(self, source, path):
		path.append(self)
		source.get("<Str>")
		self._x = source.get().value()
		source.get("</Str>")
		path.pop()

XmlFactory.instance(Atomic).registerType(Str)
XmlFactory.instance(Str).registerType(Str)