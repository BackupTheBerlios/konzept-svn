# -*- coding: UTF-8 -*-

class GraphElement:
	""" Describes a unique element of a graph.
	    Such elements belong to two mayor classes: connectors and nodes.
	"""

	nextId = 0
	def newId(self):
		id = GraphElement.nextId
		GraphElement.nextId = GraphElement.nextId + 1
		return id

	def __init__(self, id = None):
		if id == None:
			""" Generate a new id for a new element of the graph. """
			self._id = self.newId()
		else:
			""" When loading graph elements from file
			    their ids are predefined. """
			self.setId(id)

	def id(self): return self._id

	def setId(self, id):
		""" Set a predefined id. """
		""" Make shure that the next id of a new element
			equals the biggest predefined id plus 1. """
		if GraphElement.nextId <= id:
			GraphElement.nextId = id + 1
		self._id = id