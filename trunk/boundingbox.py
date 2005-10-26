# -*- coding: UTF-8 -*-

from numarray import *

class BoundingBox:
	""" Template class for all geometrical objects.
	    Provides generic coordinate calculation services.
	    Coordinates are given in discrete raster units.
	    A BoundingBox describes a rectangular area, where
	    a concrete visual object lays in and prodvides functions
	    to manipulate those rectangular area.
	"""

	def __init__(self, x0 = None, y0 = None, x1 = None, y1 = None):
		self._x0 = None
		self._y0 = None
		self._x1 = None
		self._y1 = None
		self.setCoords(x0, y0, x1, y1)
		self._orig = None

		(self._minWidth, self._minHeight) = (1, 1)
		(self._maxWidth, self._maxHeight) = (0, 0)

	def typeName(self): return "BoundingBox"

	def valid(self): return self._x0 != None and self._y0 != None and self._x1 != None and self._y1 != None

	def x0(self): return self._x0
	def y0(self): return self._y0
	def x1(self): return self._x1
	def y1(self): return self._y1
	def width(self): return self.x1() - self.x0() + 1
	def height(self): return self.y1() - self.y0() + 1
	def cx(self): return (self.x1() + self.x0()) / 2
	def cy(self): return (self.y1() + self.y0()) / 2
	def center(self): return array([self.cx(), self.cy()])

	def orig(self): return self._orig

	def setCoords(self, x0, y0, x1, y1):
		if x1 > x0:
			self._x0 = x0
			self._x1 = x1
		if y1 > y0:
			self._y0 = y0
			self._y1 = y1

	def containsPoint(self, x, y):
		b = (x >= self.x0()) & (y >= self.y0())
		b &= (x <= self.x1()) & (y <= self.y1())
		return b

	def copy(self):
		c = BoundingBox(self._x0, self._y0, self._x1, self._y1)
		c._orig = self._orig
		(c._minWidth, c._minHeight) = (self._minWidth, self._minHeight)
		(c._maxWidth, c._maxHeight) = (self._maxWidth, self._maxHeight)
		return c

	def beginTransform(self):
		self._orig = self.copy()

	def endTransform(self):
		self._orig = None

	def abortTransform(self):
		# print "BoundingBox.abortTransform()"
		o = self.orig()
		self.setCoords(o.x0(), o.y0(), o.x1(), o.y1())
		self._orig = None

	def widthOk(self, x0, x1):
		w = (x1-x0)+1
		return w >= self._minWidth and (w <= self._maxWidth or self._maxWidth == 0)

	def heightOk(self, y0, y1):
		h = (y1-y0)+1
		return h >= self._minHeight and (h <= self._maxHeight or self._maxHeight == 0)

	def getTransformX(self, fx, dx):
		o = self.orig()
		x0 = int(o.x0() + dx)
		x1 = int((o.width() - 1)  * fx + o.x0() + dx)
		return (x0, x1)

	def getTransformY(self, fy, dy):
		o = self.orig()
		y0 = int(o.y0() + dy)
		y1 = int((o.height() - 1) * fy + o.y0() + dy)
		return (y0, y1)

	def getTransform(self, fx, fy, dx, dy):
		o = self.orig()
		(x0, x1) = self.getTransformX(fx, dx)
		(y0, y1) = self.getTransformY(fy, dy)
		return (x0, y0, x1, y1)

	def wouldTransformX(self, fx, dx):
		# return self.orig().minScaleX() <= fx \
		#        and (fx <= self.orig().maxScaleX() or self.orig().maxScaleX() == 0)
		(x0, x1) = self.getTransformX(fx, 0)
		return self.widthOk(x0, x1)

	def wouldTransformY(self, fy, dy):
		# return self.orig().minScaleY() <= fy \
		#        and (fy <= self.orig().maxScaleY() or self.orig().maxScaleY() == 0)
		(y0, y1) = self.getTransformY(fy, 0)
		return self.heightOk(y0, y1)

	def wouldTransform(self, fx, fy, dx, dy):
		return self.wouldTransformX(fx, dx) or self.wouldTransformY(fy, dy)

	def updateTransformX(self, fx, dx):
		(x0, x1) = self.getTransformX(fx, dx)
		if self.widthOk(x0, x1):
			(self._x0, self._x1) = (x0, x1)

	def updateTransformY(self, fy, dy):
		(y0, y1) = self.getTransformY(fy, dy)
		if self.heightOk(y0, y1):
			(self._y0, self._y1) = (y0, y1)

	def updateTransform(self, fx, fy, dx, dy):
		self.updateTransformX(fx, dx)
		self.updateTransformY(fy, dy)

	def updateCoords(self, x0, y0, x1, y1):
		if (x0 >= x1) or (y0 >= y1): return
		o = self.orig()
		fx = float(x1 - x0 + 1) / o.width()
		fy = float(y1 - y0 + 1) / o.height()
		dx = x0 - o.x0()
		dy = y0 - o.y0()
		self.updateTransform(fx, fy, dx, dy)

	def coordsOk(self, x0, y0, x1, y1):
		w = x1 - x0 + 1
		h = y1 - y0 + 1
		if w < self._minWidth: return False
		if h < self._minHeight: return False
		if self._maxWidth != 0:
			if w > self._maxWidth: return False
		if self._maxHeight != 0:
			if h > self._maxHeight: return False
		return True

	def minSize(self):
		return (self._minWidth, self._minHeight)

	def maxSize(self):
		return (self._maxWidth, self._maxHeight)

	def setMinSize(self, minWidth, minHeight):
		(self._minWidth, self._minHeight) = (minWidth, minHeight)

	def setMaxSize(self, maxWidth, maxHeight):
		(self._maxWidth, self._maxHeight) = (maxWidth, maxHeight)

	def minWidth(self): return self._minWidth
	def maxWidth(self): return self._maxWidth
	def minHeight(self): return self._minHeight
	def maxHeight(self): return self._maxHeight

	def clampX0(self, x0, x1):
		w = x1 - x0 + 1
		minW = self.minWidth()
		maxW = self.maxWidth()
		if w < minW: x0 = x1 - minW + 1
		if maxW != 0 and w > maxW: x0 = x1 - maxW + 1
		return x0

	def clampX1(self, x0, x1):
		w = x1 - x0 + 1
		minW = self.minWidth()
		maxW = self.maxWidth()
		if w < minW: x1 = x0 + minW - 1
		if maxW != 0 and w > maxW: x1 = x0 + maxW - 1
		return x1

	def clampY0(self, y0, y1):
		h = y1 - y0 + 1
		minH = self.minHeight()
		maxH = self.maxHeight()
		if h < minH: y0 = y1 - minH + 1
		if maxH != 0 and h > maxH: y0 = y1 - maxH + 1
		return y0

	def clampY1(self, y0, y1):
		h = y1 - y0 + 1
		minH = self.minHeight()
		maxH = self.maxHeight()
		if h < minH: y1 = y0 + minH - 1
		if maxH != 0 and h > maxH: y1 = y0 + maxH - 1
		return y1

	def minScaleX(self):
		return float(self.minWidth()) / self.width()

	def minScaleY(self):
		return float(self.minHeight()) / self.height()

	def maxScaleX(self):
		return float(self.maxWidth()) / self.width()

	def maxScaleY(self):
		return float(self.maxHeight()) / self.height()

	def minScale(self):
		return max(self.minScaleX(), self.minScaleY())

	def maxScale(self):
		return min(self.maxScaleX(), self.maxScaleY())

	def writeXml(self, sink):
		sink.write("<BoundingBox>\n")
		sink.stepDown()
		sink.write("<x0>%d</x0>\n" % self.x0())
		sink.write("<y0>%d</y0>\n" % self.y0())
		sink.write("<x1>%d</x1>\n" % self.x1())
		sink.write("<y1>%d</y1>\n" % self.y1())
		sink.stepUp()
		sink.write("</BoundingBox>\n")

	def readXml(self, source, path):
		source.get("<BoundingBox>")
		source.get("<x0>")
		x0 = int(source.get().value())
		source.get("</x0>")
		source.get("<y0>")
		y0 = int(source.get().value())
		source.get("</y0>")
		source.get("<x1>")
		x1 = int(source.get().value())
		source.get("</x1>")
		source.get("<y1>")
		y1 = int(source.get().value())
		source.get("</y1>")
		self.setCoords(x0, y0, x1, y1)
		source.get("</BoundingBox>")
