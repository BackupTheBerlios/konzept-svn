# -*- coding: UTF-8 -*-

from sets import *
from graphelement import *
from nodeshape import *
from xmlfactory import *

def newNode(): return Node()

class Node(GraphElement):

	def __init__(self, shape = None, id = None):
		GraphElement.__init__(self, id)

		self._connectorSets = {}
		self._selectionFrame = None
		self.setShape(shape)

		# print "created Node", self.id()

	def staticTypeName(): return "Node"
	def typeName(self): return Node.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	newInstance = staticmethod(newNode)

	def unlink(self):
		""" A node as any other object also, may aggregate other objects.
		    Before destruction this associations should be destroyed.
		    For this purpose inherited classes may overload this method. """
		self._shape.unlink()

	def addConnectorSet(self, cs):
		# print "Node", self.id(), ": addConnectorSet()"
		self._connectorSets[cs] = cs

	def removeConnectorSet(self, cs):
		# print "Node", self.id(), ": removeConnectorSet()"
		del self._connectorSets[cs]

	def updateConnectors(self):
		for cs in self._connectorSets:
			cs.updateGeometry()

	def connectorSets(self): return self._connectorSets

	def shape(self): return self._shape

	def setShape(self, shape):
		if shape != None: shape.setNode(self)
		self._shape = shape

	def copy(self):
		b = Node()
		b.setShape(self.shape().copy())
		return b
	
	def writeXml(self, sink):
		sink.write("<Node>\n")
		sink.stepDown()
		sink.write("<id>%d</id>\n" % self.id())
		self.shape().writeXml(sink)
		sink.stepUp()
		sink.write("</Node>\n")

	def readXml(self, source, path):
		path.append(self)
		source.get("<Node>")
		source.get("<id>")
		self.setId(int(source.get().value()))
		source.get("</id>")
		shape = XmlFactory.instance(NodeShape).createFromXml(source, path)
		self.setShape(shape)
		source.get("</Node>")
		path.pop()

XmlFactory.instance(Node).registerType(Node)
