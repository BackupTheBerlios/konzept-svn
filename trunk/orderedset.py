# -*- coding: UTF-8 -*-

from xmlfactory import *
from xmltokensource import *

class OrderedSet:
	""" Ordered set interface wrapper for python's map type.
	    Based on the week assumption that python's map is
	    non-stochastic by its nature.
	    The implementation is obscure in the way, that the add() method
	    adds only copies of object references.
	"""

	def __init__(self, id = None, elementType = None, initialElements = []):
		self._id = id
		self._elementType = elementType
		self._map = {}
		self._triggers = []
		for e in initialElements:
			self.add(e)

	def staticTypeName(): return "Set"
	def typeName(self): return OrderedSet.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(args): return OrderedSet(args[0], args[1], args[2])
	newInstance = staticmethod(newInstance)

	def id(self): return self._id

	def unlinkTriggers(self):
		if self._triggers != None:
			for t in self._triggers:
				t.unlink()

	def addTrigger(self, t):
		self._triggers.append(t)
		t.init(self)

	def triggers(self): return self._triggers

	def add(self, e):
		self._map[e.id()] = e
		for t in self._triggers: t.add(self, e)

	def remove(self, e):
		del self._map[e.id()]
		for t in self._triggers: t.remove(self, e)

	def removeAll(self):
		m2 = self._map
		self._map = {}
		for k in m2:
			for t in self._triggers:
				t.remove(self, m2[k])

	def __contains__(self, e):
		return e.id() in self._map

	def __iter__(self):
		return self._map.itervalues()

	def __getitem__(self, id):
		# returns copy of the element with given id?!
		return self._map[id]

	def __setitem__(self, id, value):
		self._map[id] = value

	def copy(self, id2 = None):
		set2 = OrderedSet(id2, self._elementType)
		for k in self._map:
			set2._map[k] = self._map[k]
		return set2
	
	def deepCopy(self, id2 = None):
		set2 = OrderedSet(id2, self._elementType)
		for k in self._map:
			set2._map[k] = self._map[k].copy()
		return set2

	def top(self):
		for e in self:
			return e
	
	def count(self):
		return len(self._map)

	def combination(self):
		""" The list of all combinations of two elements
		    of this set. A combination is always a tuple of
		    two elements, where the lower element is placed
		    at lower index.
			The operational complexity is ideal O(n)=(n*n)/2.
		"""
		res = []
		n = self.count()
		for e1 in self:
			i = self.count() - n
			for e2 in self:
				if i != 0:
					i = i - 1
					continue
				res.append((e1,e2))
			n = n - 1
		return res

	def writeXml(self, sink):
		if self.id() == None: return
		sink.write("<Set>\n")
		sink.stepDown()
		sink.write("<id>"+str(self.id())+"</id>\n", )
		for e in self:
			e.writeXml(sink)
		sink.stepUp()
		sink.write("</Set>\n")

	def readXml(self, source, path):
		path.append(self)
		self.removeAll()
		source.get("<Set>")
		source.get("<id>")
		self._id = source.get().value()
		source.get("</id>")
		while source.lookAhead() != tag("</Set>"):
			element = XmlFactory.instance(self._elementType).createFromXml(source, path)
			self.add(element)
		source.get("</Set>")
		path.pop()

XmlFactory.instance(OrderedSet).registerType(OrderedSet)
