#!/usr/bin/python
# -*- coding: UTF-8 -*-

from qt import *
from mousecursors import *
from boundingbox import *

class SelectionFrame:
	""" Visible frame arround a selected node.
	"""

	def __init__(self, boundingBox):
		self._boundingBox = boundingBox

		# border thickness
		self._thickness = 8
		self.setColor(QColor(170,170,170))

	def y0Bar(self):
		r = self._boundingBox
		return BoundingBox(r.x0(), r.y0()-self._thickness, r.x1(), r.y0()-1)

	def y1Bar(self):
		r = self._boundingBox
		return BoundingBox(r.x0(), r.y1()+1, r.x1(), r.y1()+self._thickness)

	def x0Bar(self):
		r = self._boundingBox
		return BoundingBox(r.x0()-self._thickness, r.y0(), r.x0()-1, r.y1())

	def x1Bar(self):
		r = self._boundingBox
		return BoundingBox(r.x1()+1, r.y0(), r.x1()+self._thickness, r.y1())

	def x0Y0Handle(self):
		r = self._boundingBox
		return BoundingBox(r.x0()-self._thickness, r.y0()-self._thickness, r.x0()-1, r.y0()-1)

	def x0Y1Handle(self):
		r = self._boundingBox
		return BoundingBox(r.x0()-self._thickness, r.y1()+1, r.x0()-1, r.y1()+self._thickness)

	def x1Y0Handle(self):
		r = self._boundingBox
		return BoundingBox(r.x1()+1, r.y0()-self._thickness, r.x1()+self._thickness, r.y0()-1)

	def x1Y1Handle(self):
		r = self._boundingBox
		return BoundingBox(r.x1()+1, r.y1()+1, r.x1()+self._thickness, r.y1()+self._thickness)

	def setColor(self, color): self._color = color
	def color(self): return self._color
	
	def drawTo(self, p):
		r = self._boundingBox
		brush = QBrush(self.color())
		brush.setStyle(Qt.Dense4Pattern)
		p.setBrush(brush)
		p.setPen(Qt.NoPen)
		p.drawRect(r.x0()-self._thickness, r.y0()-self._thickness, r.width()+2*self._thickness, self._thickness)
		p.drawRect(r.x0()-self._thickness, r.y0(), self._thickness, r.height())
		p.drawRect(r.x0()-self._thickness, r.y1()+1, r.width()+2*self._thickness, self._thickness)
		p.drawRect(r.x1()+1, r.y0(), self._thickness, r.height())

	def containsPoint(self, x, y):
		r = self._boundingBox
		b = (x >= r.x0()-self._thickness) & (y >= r.y0()-self._thickness)
		b &= (x <= r.x1()+self._thickness) & (y <= r.y1()+self._thickness)
		return b

	def getCursor(self, x, y):
		if self.x0Bar().containsPoint(x, y) or self.x1Bar().containsPoint(x, y):
			return mouseCursors.sizeHorCursor()
		if self.y0Bar().containsPoint(x, y) or self.y1Bar().containsPoint(x, y):
			return mouseCursors.sizeVerCursor()
		if self.x0Y0Handle().containsPoint(x, y) or self.x1Y1Handle().containsPoint(x, y):
			return mouseCursors.sizeFDiagCursor()
		if self.x0Y1Handle().containsPoint(x, y) or self.x1Y0Handle().containsPoint(x, y):
			return mouseCursors.sizeBDiagCursor()
		return mouseCursors.pointingHandCursor()

