# -*- coding: UTF-8 -*-

from graph import *
from history import *

class Graph: None

class GraphHistory(History):
	def __init__(self):
		History.__init__(self, Graph)
	
	def stateChanged(self, graph): None
	def modified(self, graph): None
	def beforeModified(self, graph): self.append(graph.deepCopy())


