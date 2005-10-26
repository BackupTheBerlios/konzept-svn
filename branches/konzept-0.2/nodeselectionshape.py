# -*- coding: UTF-8 -*-

from transformframe import *
from boundingbox import *
from orderedset import *
from settrigger import *

class NodeSelectionShape(SetTrigger, BoundingBox):
	def __init__(self, nodeSelection):
		BoundingBox.__init__(self)

		self._nodeSelection = nodeSelection
		self._nodeSelection.addTrigger(self)

		self._transformFrame = None

		self._minScaleX = None
		self._minScaleY = None
		self._maxScaleX = None
		self._maxScaleY = None
		self.resetMinMaxSize()

	def add(self, set, node):
		s = node.shape()
		s.doCreateSelectionFrame()
		if self._nodeSelection.count() == 1:
			self.resetMinMaxSize()
			self.setCoords(s.x0(), s.y0(), s.x1(), s.y1())
			self._transformFrame = TransformFrame(self)
			# www.self._transformFrame.setColor(QColor(255,0,0))
		else:
			if s.x0() < self.x0(): self._x0 = s.x0()
			if s.y0() < self.y0(): self._y0 = s.y0()
			if s.x1() > self.x1(): self._x1 = s.x1()
			if s.y1() > self.y1(): self._y1 = s.y1()

	def remove(self, set, node):
		node.shape().doDestroySelectionFrame()
		if self._nodeSelection.count() == 0:
			self._transformFrame = None
		else:
			self.updateSize()

	def updateSize(self):
		for node in self._nodeSelection: break   # trick to get first node
		s = node.shape()
		self._x0 = s.x0()
		self._y0 = s.y0()
		self._x1 = s.x1()
		self._y1 = s.y1()
		for node in self._nodeSelection:
			s = node.shape()
			if s.x0() < self.x0(): self._x0 = s.x0()
			if s.y0() < self.y0(): self._y0 = s.y0()
			if s.x1() > self.x1(): self._x1 = s.x1()
			if s.y1() > self.y1(): self._y1 = s.y1()

	def drawTo(self, p):
		if self._nodeSelection.count() != 0 and self._transformFrame != None:
			self._transformFrame.drawTo(p)

	def transformFrame(self): return self._transformFrame

	def containsPoint(self, x, y):
		if (self._transformFrame != None):
			return self._transformFrame.containsPoint(x, y)
		else:
			return False

	def minScaleX(self): return self._minScaleX
	def minScaleY(self): return self._minScaleY
	def maxScaleX(self): return self._maxScaleX
	def maxScaleY(self): return self._maxScaleY

	def resetMinMaxSize(self):
		self.setMinSize(1, 1)
		self.setMaxSize(0, 0)
	
	# actually calculates _minWidth, _minHeight, _maxWidth, _maxHeight
	# which is needed for clamping (see TransformFrame)
	def updateMinMaxScale(self):
		self._minScaleX = BoundingBox.minScaleX(self)
		self._minScaleY = BoundingBox.minScaleY(self)
		self._maxScaleX = BoundingBox.maxScaleX(self)
		self._maxScaleY = BoundingBox.maxScaleY(self)
		for node in self._nodeSelection:
			s = node.shape()
			if s.minScaleX() > self._minScaleX: self._minScaleX = s.minScaleX()
			if s.minScaleY() > self._minScaleY: self._minScaleY = s.minScaleY()
			if s.maxScaleX() < self._maxScaleX: self._maxScaleX = s.maxScaleX()
			if s.maxScaleY() < self._maxScaleY: self._maxScaleY = s.maxScaleY()
		self._minWidth = int(self.width() * self._minScaleX)
		self._maxWidth = int(self.width() * self._maxScaleX)
		self._minHeight = int(self.height() * self._minScaleY)
		self._maxHeight = int(self.height() * self._maxScaleY)
		"""print "updateMinMaxScale()"
		print "self._minWidth = ", self._minWidth
		print "self._maxWidth = ", self._maxWidth
		print "self._minHeight = ", self._minHeight
		print "self._maxHeight = ", self._maxHeight"""
		#print "self.minScaleX(), self.maxScaleX() = ", (self.minScaleX(), self.maxScaleX())
		#print "self.minScaleY(), self.maxScaleY() = ", (self.minScaleY(), self.maxScaleY())

	def getCursor(self, x, y):
		if (self._transformFrame != None):
			return self._transformFrame.getCursor(x, y)
		return mouseCursors.pointingHandCursor()

	def wouldTransformX(self, fx, dx):
		# return self.minScaleX() <= fx and (fx <= self.maxScaleX() or self.maxScaleX() == 0)
		for node in self._nodeSelection:
			if not node.shape().wouldTransformX(fx, 0): return False
		return True

	def wouldTransformY(self, fy, dy):
		# return self.minScaleY() <= fy and (fy <= self.maxScaleY() or self.maxScaleY() == 0)
		for node in self._nodeSelection:
			if not node.shape().wouldTransformY(fy, 0): return False
		return True

	def beginTransform(self):
		# print "selection.beginTransform()"
		BoundingBox.beginTransform(self)
		for node in self._nodeSelection:
			node.shape().beginTransform()
		self.updateMinMaxScale()

	def endTransform(self):
		# print "selection.endTransform()"
		BoundingBox.endTransform(self)
		for node in self._nodeSelection:
			node.shape().endTransform()
		self.updateSize()

	def abortTransform(self):
		# print "selection.abortTransform()"
		BoundingBox.abortTransform(self)
		for node in self._nodeSelection:
			node.shape().abortTransform()
		self.updateSize()

	def updateTransformX(self, fx, dx):
		BoundingBox.updateTransformX(self, fx, dx)
		for node in self._nodeSelection:
			rx0 = float((node.shape().orig().x0() - self.orig().x0()))
			dxr = rx0 * fx - rx0 + dx
			node.shape().updateTransformX(fx, dxr)

	def updateTransformY(self, fy, dy):
		BoundingBox.updateTransformY(self, fy, dy)
		for node in self._nodeSelection:
			ry0 = float((node.shape().orig().y0() - self.orig().y0()))
			dyr = ry0 * fy - ry0 + dy
			node.shape().updateTransformY(fy, dyr)

	def updateTransform(self, fx, fy, dx, dy):
		# print "selection.updateTransform(%f, %f, %f, %f)" % (fx, fy, dx, dy)
		BoundingBox.updateTransform(self, fx, fy, dx, dy)
		
		for node in self._nodeSelection:
			rx0 = float((node.shape().orig().x0() - self.orig().x0()))
			dxr = rx0 * fx - rx0 + dx
			ry0 = float((node.shape().orig().y0() - self.orig().y0()))
			dyr = ry0 * fy - ry0 + dy
			node.shape().updateTransform(fx, fy, dxr, dyr)
