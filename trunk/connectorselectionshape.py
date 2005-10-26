# -*- coding: UTF-8 -*-

from qt import *
from connectorselectionframe import *
from orderedset import *
from settrigger import *

class ConnectorSelectionShape(SetTrigger):
	""" Extends the set of selected nodes with GUI logic
	    by delegation based inheritance. """

	def __init__(self, connectorSelection):
		self._connectorSelection = connectorSelection
		self._connectorSelection.addTrigger(self)

	def add(self, set, connector):
		connector.shape().doCreateSelectionFrame()

	def remove(self, set, connector):
		connector.shape().doDestroySelectionFrame()

	def drawTo(self, p):
		for connector in self._connectorSelection:
			connector.shape().selectionFrame().drawTo(p)

	def connectorBelowCursor(self, x, y):
		for connector in self._connectorSelection:
			if connector.shape().containsPoint(x,y): return connector
		return None
