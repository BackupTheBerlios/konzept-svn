# -*- coding: UTF-8 -*-

from xmlfactory import *
from boxshape import *
from rectangleshape import *
from qt import *
from math import *
from orderedset import *
from list import *

class BoxColumnShape(RectangleShape):
	def __init__(self, x0 = None, y0 = None, x1 = None, y1 = None, numRow = None):
		RectangleShape.__init__(self, x0, y0, x1, y1)
		
		self._numRow = numRow
		self._column = List("column", BoxShape)
		
		self.setHMargin(10)
		self.setVMargin(8)
		
		if numRow != None:
			w = self.width()
			h = self.height()/numRow
			(x, y) = (x0, y0)
			for i in range(numRow):
				bs = BoxShape(x, y, x + w, y + h)
				self._column.append(bs)
				y = y + h
		
		# where the inline text editor currently is placed on
		self._activeBoxShape = None

	def staticTypeName(): return "BoxColumnShape"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return BoxColumnShape()
	newInstance = staticmethod(newInstance)

	def typeName(self): return BoxColumnShape.staticTypeName()

	def column(self): return self._column
	
	def copy(self):
		s2 = BoxColumnShape(self.x0(), self.y0(), self.x1(), self.y1())
		s2._column = List("column", BoxShape)
		for bs in self.column():
			bs2 = bs.copy()
			s2._column.append(bs2)
		return s2
	
	def moveCenter(self, cx, cy):
		dx = cx - self.cx()
		dy = cy - self.cy()
		RectangleShape.moveCenter(self, cx, cy)
		for bs in self.column():
			bs.moveCenter(bs.cx()+dx, bs.cy()+dy)
		
	def resize(self, w2, h2): 
		fx = float(w2) / self.width()
		fy = float(h2) / self.height()
		dx = self.width() - w2
		dy = self.height() - h2
		self.beginTransform()
		self.updateTransform(fx, fy, dx, dy)
		self.endTransform()
	
	def selectActive(self, cursorX = None, cursorY = None):
		if cursorX == None:
			self._activeBoxShape = None
			return 
		for bs in self.column():
			if bs.containsPoint(cursorX, cursorY):
				self._activeBoxShape = bs
				break
		if self._activeBoxShape == None:
			# we should reject the request!, but lets go on with default
			self._activeBoxShape = self.column().top()
		bs = self._activeBoxShape
	
	def text(self): return self._activeBoxShape.text()
	def setText(self, s): self._activeBoxShape.setText(s)
		
	def textAlign(self): return self._activeBoxShape.textAlign()
	def setTextAlign(self, align):
		if self._activeBoxShape == None:
			for bs in self.column():
				bs.setTextAlign(align)
		else:
			self._activeBoxShape.setTextAlign(align)
	
	def bgColor(self): return self.column().top().bgColor()
	def setBgColor(self, color):
		for bs in self.column():
			bs.setBgColor(color)
	
	def hMargin(self): return self.column().top().hMargin()
	def setHMargin(self, hm): 
		for bs in self.column():
			bs.setHMargin(hm)
	
	def vMargin(self): return self.column().top().vMargin()
	def setVMargin(self, vm):
		for bs in self.column():
			bs.setVMargin(vm)
	
	def boundingBoxOfText(self):
		bs = self._activeBoxShape
		return BoundingBox(bs.x0()+bs.hMargin(), bs.y0()+bs.vMargin(), bs.x1()-bs.hMargin(), bs.y1()-bs.vMargin())
	
	def beginInlineTextEdit(self): 
		self._activeBoxShape.beginInlineTextEdit()
		
	def endInlineTextEdit(self): 
		self._activeBoxShape.endInlineTextEdit()
	
	def optimizeSize(self):
		w2 = 0
		h2 = 0
		for bs in self.column():
			bs.optimizeSize()
			if bs.width() > w2: w2 = bs.width()
			h2 = h2 + bs.height() - 1
		x0 = self.cx() - w2/2
		x1 = self.cx() + w2/2
		y0 = self.cy() - h2/2
		y1 = self.cy() + h2/2
		self.setCoords(x0, y0, x1, y1)
		
		for bs in self.column():
			y1 = y0 + bs.height() - 1
			bs.setCoords(x0, y0, x1, y1)
			bs.updateGeometry()
			y0 = y1
			
		self.updateGeometry()
		
	def updateSize(self):
		for bs in self.column(): break 
		self._x0 = bs.x0()
		self._y0 = bs.y0()
		self._x1 = bs.x1()
		self._y1 = bs.y1()
		for bs in self.column():
			if bs.x0() < self.x0(): self._x0 = bs.x0()
			if bs.y0() < self.y0(): self._y0 = bs.y0()
			if bs.x1() > self.x1(): self._x1 = bs.x1()
			if bs.y1() > self.y1(): self._y1 = bs.y1()
	
	def beginTransform(self):
		RectangleShape.beginTransform(self)
		for bs in self.column():
			bs.beginTransform()

	def endTransform(self):
		RectangleShape.endTransform(self)
		for bs in self.column():
			bs.endTransform()
		self.updateSize()

	def abortTransform(self):
		RectangleShape.abortTransform(self)
		for bs in self.column():
			bs.abortTransform()
	
	"""def wouldTransformY(self, fy, dy):
		if fy != 1: return False
		else: return True"""

	def updateTransformX(self, fx, dx):
		RectangleShape.updateTransformX(self, fx, dx)
		for bs in self.column():
			bs.updateTransformX(fx, dx)

	def updateTransformY(self, fy, dy):
		RectangleShape.updateTransformY(self, fy, dy)
		for bs in self.column():
			ry0 = float((bs.orig().y0() - self.orig().y0()))
			dyr = ry0 * fy - ry0 + dy
			bs.updateTransformY(fy, dyr)

	def updateTransform(self, fx, fy, dx, dy):
		RectangleShape.updateTransform(self, fx, fy, dx, dy)
		for bs in self.column():
			ry0 = float((bs.orig().y0() - self.orig().y0()))
			dyr = ry0 * fy - ry0 + dy
			bs.updateTransform(fx, fy, dx, dyr)

	def translate(self, dx, dy):
		RectangleShape.translate(self, dx, dy)
		for bs in self.column():
			bs.translate(dx, dy)
		
	def drawTo(self, p):
		for bs in self.column():
			bs.drawTo(p)
		if self._selectionFrame != None:
			self._selectionFrame.drawTo(p)

	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		sink.stepDown()
		self.column().writeXml(sink)
		sink.stepUp()
		sink.write("</%s>\n" % self.typeName())

	def readXml(self, source, path):
		path.append(self)
		source.get("<%s>" % self.typeName())
		self._column = XmlFactory.instance(List).createFromXml(source, path, ("column", NodeShape, []))
		source.get("</%s>" % self.typeName())
		self.updateSize()
		self.updateGeometry()
		path.pop()

XmlFactory.instance(NodeShape).registerType(BoxColumnShape)
