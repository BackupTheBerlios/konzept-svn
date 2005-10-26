# -*- coding: UTF-8 -*-

from numarray import *
from linesegment import *
from graphelement import *
from xmlfactory import *
from connectorshape import *

def newConnector(): return Connector()

class Connector(GraphElement):
	""" connects two nodes,
	    provides start and end point calculation,
	    informs connected nodes about connection establishment """

	def __init__(self, shape = None, id = None):
		GraphElement.__init__(self, id)

		self._node0 = None   # from node
		self._node1 = None   # to node
		self._shape = shape

	def staticTypeName(): return "Connector"
	def typeName(self): return Connector.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	newInstance = staticmethod(newConnector)

	def shape(self): return self._shape

	def node0(self): return self._node0
	def node1(self): return self._node1

	def setNode0(self, node0): self._node0 = node0
	def setNode1(self, node1): self._node1 = node1

	def dragP0(self, p0):
		""" deliver new drag position of p0 and calculate p1 accordingly """

		# calculate p1
		center1 = self._node1.shape().center()
		ls = LineSegment(p0, center1)
		intersection = self._node0.shape().intersectionWithLineSegment(ls)
		if intersection != []: q = intersection.pop()
		else: q = None
		# if q == None: q = center1
		self._shape.setP0P1(p0, q)
		self._shape.updateGeometry()

	def dragP1(self, p1):
		""" deliver new drag position of p1 and calculate p0 accordingly """

		# calculate p0
		center0 = self._node0.shape().center()
		ls = LineSegment(p1, center0)
		intersection = self._node0.shape().intersectionWithLineSegment(ls)
		if intersection != []: q = intersection.pop()
		else: q = None
		# if q == None: q = center0
		self._shape.setP0P1(q, p1)
		self._shape.updateGeometry()

	def calcP0P1(self):
		""" calculate the start and the end point
		    of the connection line between the two nodes """
		if self._node0 == None or self._node1 == None: return
		ls = LineSegment(self._node0.shape().center(), self._node1.shape().center())

		intersection = self._node0.shape().intersectionWithLineSegment(ls)
		if intersection != []: q0 = intersection.pop()
		else: q0 = self._node0.shape().center()

		intersection = self._node1.shape().intersectionWithLineSegment(ls)
		if intersection != []: q1 = intersection.pop()
		else: q1 = self._node1.shape().center()

		self._shape.setP0P1(q0, q1)
		self._shape.updateGeometry()

	def writeXml(self, sink):
		sink.write("<Connector>\n")
		sink.stepDown()
		sink.write("<id>%d</id>\n" % self.id())
		self.shape().writeXml(sink)
		sink.stepUp()
		sink.write("</Connector>\n")

	def readXml(self, source, path):
		path.append(self)
		source.get("<Connector>")
		source.get("<id>")
		self.setId(int(source.get().value()))
		source.get("</id>")
		connectorSet = path[-3]
		if path[-2].id() == "positiveConnectors":
			self._node0 = connectorSet.node0()
			self._node1 = connectorSet.node1()
		else:
			self._node0 = connectorSet.node1()
			self._node1 = connectorSet.node0()
		self._shape = XmlFactory.instance(ConnectorShape).createFromXml(source, path)
		source.get("</Connector>")
		path.pop()

XmlFactory.instance(Connector).registerType(Connector)

