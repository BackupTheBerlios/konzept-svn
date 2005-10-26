# -*- coding: UTF-8 -*-

from xmlfactory import *
from xmltokensource import *
from atomics import *

class Map:
	def __init__(self, id = None, keyType = None, valueType = None):
		self._id = id
		self._keyType = keyType
		self._valueType = valueType
		self._m = {}
		
	def id(self): return self._id
	
	def staticTypeName(): return "Map"
	def typeName(self): return Map.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(args = None): 
		if args == None:    
			return Map()
		else:
			return Map(args[0], args[1], args[2])
	newInstance = staticmethod(newInstance)
	
	def __iter__(self): return self._m.__iter__()
	
	def __contains__(self, x):
		if type(x) == int: x = Int(x)
		elif type(x) == float: x = Float(x)
		elif type(x) == str: x = Str(x)
		elif type(x) == unicode: x = Str(str(x))
		return x in self._m

	def __getitem__(self, x):
		if type(x) == int: x = Int(x)
		elif type(x) == float: x = Float(x)
		elif type(x) == str: x = Str(x)
		y = self._m[x]
		if y.__class__ in [Int, Str, Float]: y = y.value()
		return y
	
	def __setitem__(self, x, y): 
		if type(x) == int: x = Int(x)
		elif type(x) == float: x = Float(x)
		elif type(x) == str: x = Str(x)
		elif type(x) == unicode: x = Str(str(x))
		if type(y) == int: y = Int(y)
		elif type(y) == float: y = Float(y)
		elif type(y) == str: y = Str(y)
		elif type(y) == unicode: y = Str(str(y))
		self._m[x] = y

	# def __getitem__(self, x): return self._m[x]
	# def __setitem__(self, x, v): self._m[x] = v
	
	def count(self): return len(self._m)
	
	def remove(self, x): 
		if type(x) == int: x = Int(x)
		elif type(x) == float: x = Float(x)
		elif type(x) == str: x = Str(x)
		elif type(x) == unicode: x = Str(str(x))
		del self._m[x]
	
	def removeAll(self): self._m = {}
	
	def copy(self):
		m2 = Map()
		for k in self._m:
			m2._m[k] = self._m[k]
		return m2
	
	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		sink.stepDown()
		if self.id() != None:
			sink.write("<id>%s</id>\n" % self.id())
		for k in self._m:
			v = self._m[k]
			sink.write("<pair>\n")
			sink.stepDown()
			k.writeXml(sink)
			v.writeXml(sink)
			sink.stepUp()
			sink.write("</pair>\n")
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
			source.get("<pair>")
			k = XmlFactory.instance(self._keyType).createFromXml(source, path)
			v = XmlFactory.instance(self._valueType).createFromXml(source, path)
			self._m[k] = v
			source.get("</pair>")
		source.get("</%s>" % self.typeName())
		path.pop()

XmlFactory.instance(Map).registerType(Map)
