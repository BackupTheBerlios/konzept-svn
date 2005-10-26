#!/usr/bin/python
# -*- coding: UTF-8 -*-

from qt import *

class ConnectorSelectionFrame:
	def __init__(self, shape):
		self._shape = shape
		self._thickness = 9

	def drawTo(self, p):
		brush = QBrush()
		brush.setColor(QColor(170,170,170))
		brush.setStyle(Qt.Dense4Pattern)
		p.setBrush(brush)
		p.setPen(Qt.NoPen)

		p.drawRect(self._shape.p0()[0]-self._thickness/2, self._shape.p0()[1]-self._thickness/2, \
		           self._thickness, self._thickness)
		p.drawRect(self._shape.p1()[0]-self._thickness/2, self._shape.p1()[1]-self._thickness/2, \
		           self._thickness, self._thickness)
