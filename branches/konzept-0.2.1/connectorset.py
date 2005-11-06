# -*- coding: UTF-8 -*-

from sets import *
from orderedset import *
from connector import *
from linesegment import *
from math import *
from numarray import *
from numarray.linear_algebra import *
from numarray_accel import *
from coordinatesystem import *
from line import *
from node import *
from xmlfactory import *

def newConnectorSet(): return ConnectorSet()

class ConnectorSet:
	""" the set of all connectors connecting two nodes """

	def __init__(self, node0 = None, node1 = None):
		self._node0 = node0
		self._node1 = node1
		self._positiveConnectors = OrderedSet("positiveConnectors", Connector)
		self._negativeConnectors = OrderedSet("negativeConnectors", Connector)

		if node0 == None or node1 == None:
			self._id = None
		else:
			self._id = self.newId(self._node0.id(), self._node1.id())

	def staticTypeName(): return "ConnectorSet"
	def typeName(self): return ConnectorSet.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	newInstance = staticmethod(newConnectorSet)

	def id(self): return self._id

	def newId(self, id0, id1):
		if id1 > id0:
			h = id1
			id1 = id0
			id0 = h
		# ugly hack, I know!!!, but anyway in C++ we will have no 
		# restriction to use 32 bit integer hash values!
		return (float(id1) * 65536 + float(id0)).__hash__()

	def __hash__(self): return self._id
	def __cmp__(self, b): return self._id - b._id

	def node0(self): return self._node0
	def node1(self): return self._node1

	def positiveConnectors(self): return self._positiveConnectors
	def negativeConnectors(self): return self._negativeConnectors

	def connectToNodes(self):
		if self._node0 != None: self._node0.addConnectorSet(self)
		if self._node1 != None: self._node1.addConnectorSet(self)

	def detachFromNodes(self):
		if self._node0 != None: self._node0.removeConnectorSet(self)
		if self._node1 != None: self._node1.removeConnectorSet(self)
		self._node0 = None
		self._node1 = None

	def addPositiveConnector(self, c):
		self._positiveConnectors.add(c)
		self.updateGeometry()

	def addNegativeConnector(self, c):
		self._negativeConnectors.add(c)
		self.updateGeometry()

	def removePositiveConnector(self, c):
		self._positiveConnectors.remove(c)
		self.updateGeometry()

	def removeNegativeConnector(self, c):
		self._negativeConnectors.remove(c)
		self.updateGeometry()

	def addConnector(self, c):
		if self._node0 == c._node0:
			self.addPositiveConnector(c)
		else:
			self.addNegativeConnector(c)

	def removeConnector(self, c):
		if self._node0 == c._node0:
			self.removePositiveConnector(c)
		else:
			self.removeNegativeConnector(c)

	def contains(self, c):
		if self._node0 == c._node0:
			return c in self._positiveConnectors
		else:
			return c in self._negativeConnectors

	def updateGeometry(self):
		# print "ConnectorSet", self._node0.id(), self._node1.id(), ": updateGeometry()"

		# ensure that n0 is always above n1
		# (to get a less complex uniform look)

		n0 = self._node0
		n1 = self._node1

		"""if abs(n1.shape().cx() - n0.shape().cx()) < abs(n1.shape().cy() - n0.shape().cy()):
			if n1.shape().cy() < n0.shape().cy():
				n0 = self._node1
				n1 = self._node0
		else:
			if n1.shape().cx() < n0.shape().cx():
				n0 = self._node1
				n1 = self._node0"""

		shape0 = n0.shape().copy()
		shape1 = n1.shape().copy()
		c0 = shape0.center()
		c1 = shape1.center()

		u = c1 - c0
		v = array([-u[1], u[0]])
		o = c0
		sys = CoordinateSystem(u, v, o)
		sys.norm()

		d0 = determinant(sys.base())
		if d0 == 0: return
		ib = inverse(sys.base(), d0)
		shape0.transform(ib)
		shape1.transform(ib)
		y0 = max(shape0.y0(), shape1.y0())
		y1 = min(shape0.y1(), shape1.y1())

		n = self._positiveConnectors.count() + self._negativeConnectors.count()
		if n == 0: return
		dy = (y1 - y0) / n

		y = y0 + dy/2

		for c in self._positiveConnectors:
			l = Line(array([0, y ]), array([1, y]))
			intersection = array(shape0.intersectionWithLine(l))

			# get the point with maximum x-value
			maxP = intersection[0]
			for i in range(1, len(intersection)):
				q = intersection[i]
				if maxP[0] < q[0]: maxP = q
			#print maxP

			intersection = array(shape1.intersectionWithLine(l))
			# get the point with minimum x-value
			minP = intersection[0]
			for i in range(1, len(intersection)):
				q = intersection[i]
				if minP[0] > q[0]: minP = q

			maxP = matrixmultiply(sys.base(), [maxP[0], maxP[1], 1])[0:2]
			minP = matrixmultiply(sys.base(), [minP[0], minP[1], 1])[0:2]

			if n0 == self._node0:
				c.shape().setP0P1(maxP, minP)
			else:
				c.shape().setP0P1(minP, maxP)
			c.shape().updateGeometry()

			y = y + dy

		for c in self._negativeConnectors:
			l = Line(array([0, y ]), array([1, y]))

			intersection = array(shape0.intersectionWithLine(l))
			if len(intersection) == 0: continue
			# get the point with maximum x-value
			maxP = intersection[0]
			for i in range(1, len(intersection)):
				q = intersection[i]
				if maxP[0] < q[0]: maxP = q
			#print maxP

			intersection = array(shape1.intersectionWithLine(l))
			if len(intersection) == 0: continue
			# get the point with minimum x-value
			minP = intersection[0]
			for i in range(1, len(intersection)):
				q = intersection[i]
				if minP[0] > q[0]: minP = q

			maxP = matrixmultiply(sys.base(), [maxP[0], maxP[1], 1])[0:2]
			minP = matrixmultiply(sys.base(), [minP[0], minP[1], 1])[0:2]

			if n0 == self._node0:
				c.shape().setP0P1(minP, maxP)
			else:
				c.shape().setP0P1(maxP, minP)
			c.shape().updateGeometry()

			y = y + dy

	def drawTo(self, p):
		for c in self._positiveConnectors:
			c.shape().drawTo(p)
			if c.shape().selectionFrame() != None:
				c.shape().selectionFrame().drawTo(p)
		for c in self._negativeConnectors:
			c.shape().drawTo(p)
			if c.shape().selectionFrame() != None:
				c.shape().selectionFrame().drawTo(p)

	def containsPoint(self, x, y):
		for c in self._positiveConnectors:
			if c.shape().containsPoint(x,y): return True
		for c in self._negativeConnectors:
			if c.shape().containsPoint(x,y): return True
		return False

	def connectorBelowCursor(self, x, y):
		for c in self._positiveConnectors:
			if c.shape().containsPoint(x,y): return c
		for c in self._negativeConnectors:
			if c.shape().containsPoint(x,y): return c
		return None

	def writeXml(self, sink):
		sink.write("<ConnectorSet>\n")
		sink.stepDown()
		sink.write("<id>\n")
		sink.stepDown()
		sink.write("<node0>%d</node0>\n" % self.node0().id())
		sink.write("<node1>%d</node1>\n" % self.node1().id())
		sink.stepUp()
		sink.write("</id>\n")
		self.positiveConnectors().writeXml(sink)
		self.negativeConnectors().writeXml(sink)
		sink.stepUp()
		sink.write("</ConnectorSet>\n")

	def readXml(self, source, path):
		path.append(self)
		source.get("<ConnectorSet>")
		source.get("<id>")
		source.get("<node0>")
		id0 = int(source.get().value())
		source.get("</node0>")
		source.get("<node1>")
		id1 = int(source.get().value())
		source.get("</node1>")
		source.get("</id>")
		self._id = self.newId(id0, id1)
		self._node0 = path[-3]._nodes[id0]
		self._node1 = path[-3]._nodes[id1]
		self._positiveConnectors = XmlFactory.instance(OrderedSet).createFromXml(source, path, ("positiveConnectors", Connector, []))
		self._negativeConnectors = XmlFactory.instance(OrderedSet).createFromXml(source, path, ("negativeConnectors", Connector, []))
		self.connectToNodes()
		self.updateGeometry()
		source.get("</ConnectorSet>")
		path.pop()

XmlFactory.instance(ConnectorSet).registerType(ConnectorSet)

