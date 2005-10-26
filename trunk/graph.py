# -*- coding: UTF-8 -*-

from orderedset import *
from connectorset import *
from node import *
from connectorset import *
from graphtrigger import *
from graphhistory import *
from xmlfactory import *

class Graph:
	def __init__(self):
		self._nodes = OrderedSet("nodes", Node)
		self._connectorSets = OrderedSet("connectorSets", ConnectorSet)
		self._nodeSelection = OrderedSet("nodeSelection", Node)
		self._connectorSelection = OrderedSet("connectorSelection", Connector)
		
		# When a new node or connector is created the default
		# shape and semantics is created by copying the prototypes.
		self._nodeShapePrototype = None
		self._nodeSemanticsPrototype = None
		self._connectorShapePrototype = None
		self._connectorSemanticsPrototype = None
		
		# Each modification or state change of graph is reported to its trigger.
		self._history = GraphHistory()
		self._trigger = [self._history]
	
	def staticTypeName(): return "Graph"
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return Graph()
	newInstance = staticmethod(newInstance)
	def typeName(self): return Graph.staticTypeName()
	
	def nodes(self): return self._nodes
	def connectorSets(self): return self._connectorSets
	def nodeSelection(self): return self._nodeSelection
	def connectorSelection(self): return self._connectorSelection

	def history(self): return self._history
	
	def nodeShapePrototype(self): return self._nodeShapePrototype
	def nodeSemanticsPrototype(self): return self._nodeSemanticsPrototype
	def connectorShapePrototype(self): return self._connectorShapePrototype
	def connectorSemanticsPrototype(self): return self._connectorSemanticsPrototype
	
	def setNodeShapePrototype(self, shape): self._nodeShapePrototype = shape
	def setNodeSemanticsPrototype(self, semantics): self._nodeSemanticsPrototype = semantics
	def setConnectorShapePrototype(self, shape): self._connectorShapePrototype = shape
	def setConnectorSemanticsPrototype(self, semantics): self._connectorSemanticsPrototype = semantics

	# ==== private graph interface
	
	def _addNode(self, node): self.nodes().add(node)
	
	def _addConnector(self, connector):
		cs = ConnectorSet(connector.node0(), connector.node1())
		if cs not in self._connectorSets:
			self._connectorSets.add(cs)
			cs.connectToNodes()
		self._connectorSets[cs.id()].addConnector(connector)

	def _addToNodeSelection(self, node):
		self.nodeSelection().add(node)
	
	def _addToConnectorSelection(self, connector):
		self.connectorSelection().add(connector)
	
	def _deleteSelectedNodes(self):
		for node in self._nodeSelection:
			self._nodes.remove(node)
			for cs in node._connectorSets.copy():
				for c in cs.positiveConnectors():
					if c in self._connectorSelection:
						self._connectorSelection.remove(c)
				for c in cs.negativeConnectors():
					if c in self._connectorSelection:
						self._connectorSelection.remove(c)
				cs.detachFromNodes()
				self._connectorSets.remove(cs)
			node.unlink()
			node = None

	def _deleteSelectedConnectors(self):
		for connector in self._connectorSelection.copy():
			self._connectorSelection.remove(connector)
			for cs in self._connectorSets.copy():
				if cs.contains(connector):
					cs.removeConnector(connector)
					if cs.positiveConnectors().count() == 0 \
					and cs.negativeConnectors().count() == 0:
						cs.detachFromNodes()
						self._connectorSets.remove(cs)

	def _unselectAll(self):
		self._connectorSelection.removeAll()
		self._nodeSelection.removeAll()

	def _insertGraph(self, g2):
		""" Inserts a second graph into this graph.
		    The new graph is selected by default to support
		    immediate move transform. """
		m = {}       # maps g2 node ids to new nodes
		for node in g2.nodes():
			node2 = node.copy()
			m[node.id()] = node2
			self._addNode(node2)
			self._addToNodeSelection(node2)
		for cs in g2.connectorSets():
			for c in cs.positiveConnectors():
				c2 = Connector(c.shape().copy())
				c2.setNode0(m[c.node0().id()])
				c2.setNode1(m[c.node1().id()])
				c2.calcP0P1()
				self._addConnector(c2)
			for c in cs.negativeConnectors():
				c2 = Connector(c.shape().copy())
				c2.setNode0(m[c.node0().id()])
				c2.setNode1(m[c.node1().id()])
				c2.calcP0P1()
				self._addConnector(c2)
	
	def _insertGraph2(self, g2):
		""" Performance tuned version of _insertGraph()
		"""
		m = {}       # maps g2 node ids to new nodes
		for node in g2._nodes:
			node2 = node.copy()
			m[node._id] = node2
			self._addNode(node2)
			self._addToNodeSelection(node2)
		for cs in g2._connectorSets:
			node0 = m[cs._node0._id]
			node1 = m[cs._node1._id]
			cs2 = ConnectorSet(node0, node1)
			self._connectorSets.add(cs2)
			cs2.connectToNodes()
			for c in cs._positiveConnectors:
				c2 = Connector(c.shape().copy())
				c2._node0 = node0
				c2._node1 = node1
				cs2._positiveConnectors.add(c2)
			for c in cs._negativeConnectors:
				c2 = Connector(c.shape().copy())
				c2._node0 = node1
				c2._node1 = node0
				cs2._negativeConnectors.add(c2)
	
	# ==== multiplexer
	
	def beforeModified(self): 
		for t in self._trigger:
			t.beforeModified(self)
	
	def modified(self): 
		for t in self._trigger:
			t.modified(self)
			
	def stateChanged(self):
		for t in self._trigger:
			t.stateChanged(self)
	
	# ==== public graph interface
	
	def createNode(self, x0, y0):
		self.beforeModified()
		shape = self.nodeShapePrototype().copy()
		shape.translate(x0, y0)
		node = Node(shape)
		self._addNode(node)
		self._unselectAll()
		self._addToNodeSelection(node)
		self.modified()
		
	def addConnector(self, connector):
		self.beforeModified()
		self._addConnector(connector)
		self.modified()
	
	def selectSingleNode(self, node):
		self._unselectAll()
		self._addToNodeSelection(node)
		self.stateChanged()
	
	def selectSingleConnector(self, connector):
		self._unselectAll()
		self._addToConnectorSelection(connector)
		self.stateChanged()
	
	def unselectAll(self):
		self._connectorSelection.removeAll()
		self._nodeSelection.removeAll()
		self.stateChanged()
	
	def addToNodeSelection(self, node):
		self.nodeSelection().add(node)
		self.stateChanged()
	
	def addToConnectorSelection(self, connector):
		self.connectorSelection().add(connector)
		self.stateChanged()
	
	def removeFromNodeSelection(self, node):
		self.nodeSelection().remove(node)
		self.stateChanged()
	
	def removeFromConnectorSelection(self, connector):
		self.connectorSelection().remove(connector)
		self.stateChanged()

	def deleteSelection(self):
		self.beforeModified()
		self._deleteSelectedNodes()
		self._deleteSelectedConnectors()
		self._unselectAll()
		self.modified()

	def somethingSelected(self):
		return self.connectorSelection().count() + self.nodeSelection().count() != 0

	def copySelection(self):
		""" creates a new graph from the selection """
		g2 = Graph()
		m = {}       # maps old node ids to new nodes
		for node in self.nodeSelection():
			node2 = node.copy()
			m[node.id()] = node2
			g2._addNode(node2)
		for t in self.nodeSelection().combination():
			cx = ConnectorSet(t[0], t[1])
			if cx in self.connectorSets():
				cs = self.connectorSets()[cx.id()]
				for c in cs.positiveConnectors():
					c2 = Connector(c.shape().copy())
					c2.setNode0(m[c.node0().id()])
					c2.setNode1(m[c.node1().id()])
					c2.calcP0P1()
					g2._addConnector(c2)
				for c in cs.negativeConnectors():
					c2 = Connector(c.shape().copy())
					c2.setNode0(m[c.node0().id()])
					c2.setNode1(m[c.node1().id()])
					c2.calcP0P1()
					g2._addConnector(c2)
		return g2
	
	def insertGraph(self, g2):
		self.beforeModified()
		self._insertGraph(g2)
		self.modified()
	
	# ==== copying and serialization
		
	def shallowCopy(self):
		g2 = Graph()
		g2._nodes = graph2.nodes()
		g2._connectorSets = graph2.connectorSets()
		return g2
	
	def deepCopy(self):
		g2 = Graph()
		g2._nodeShapePrototype = self._nodeShapePrototype
		g2._nodeSemanticsPrototype = self._nodeSemanticsPrototype 
		g2._connectorShapePrototype = self._connectorShapePrototype
		g2._connectorSemanticsPrototype = self._connectorSemanticsPrototype
		g2._history = self._history
		g2._trigger = self._trigger
		g2._insertGraph2(self)
		# g2.unselectAll()
		return g2
	
	def writeXml(self, sink):
		sink.write("<Graph>\n")
		sink.stepDown()
		self.nodes().writeXml(sink)
		self.connectorSets().writeXml(sink)
		sink.stepUp()
		sink.write("</Graph>\n")

	def readXml(self, source, path = []):
		path.append(self)
		source.get("<Graph>")
		self.unselectAll()
		self._nodes = XmlFactory.instance(OrderedSet).createFromXml(source, path, initParams = ("nodes", Node, []))
		self._connectorSets = XmlFactory.instance(OrderedSet).createFromXml(source, path, initParams = ("connectorSets", ConnectorSet, []))
		source.get("</Graph>")
		path.pop()

XmlFactory.instance(Graph).registerType(Graph)
