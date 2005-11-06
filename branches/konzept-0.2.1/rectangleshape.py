# -*- coding: UTF-8 -*-

from qt import *
from mousecursors import *
from polygonshape import *
from numarray import *

class RectangleShape(PolygonShape):
	def __init__(self, x0 = None, y0 = None, x1 = None, y1 = None):
		PolygonShape.__init__(self)

		self.setMinSize(10, 10)
		self.setMaxSize(0, 0)

		if x0 == None or y0 == None or x1 == None or y1 == None: return

		x1 = self.clampX1(x0, x1)
		y1 = self.clampY1(y0, y1)

		pa = array([[x0, y0],
		            [x0, y1],
		            [x1, y1],
		            [x1, y0]])
		self.setPoints(pa)

	def drawTo(self, p):
		PolygonShape.drawTo(self, p)
		if self._selectionFrame != None:
			self._selectionFrame.drawTo(p)

	def containsPoint(self, x, y):
		return ( x >= self.x0() and y >= self.y0() and \
		         x <= self.x1() and y <= self.y1() );
		#return PolygonShape.containsPoint(self, x, y)

	def getCursor(self, x, y):
		return mouseCursors.pointingHandCursor()

	def updateGeometry(self):
		pa = array([[self.x0(), self.y0()],
		            [self.x0(), self.y1()],
		            [self.x1(), self.y1()],
		            [self.x1(), self.y0()]])
		self.setPoints(pa)
