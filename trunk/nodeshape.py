# -*- coding: UTF-8 -*-

from qt import *
from selectionframe import *
from boundingbox import *
from xmltokensource import *
from indentsink import *
from graphelement import *

class NodeShape(BoundingBox, GraphElement):
	""" generic description of a node's shape """

	def __init__(self, id = None):
		BoundingBox.__init__(self)
		GraphElement.__init__(self, id)
		
		self._node = None
		self._selectionFrame = None
		self._text = ""

		self._inlineEditMode = False
		
	def typeName(self): return "NodeShape"

	def selectionFrame(self): return self._selectionFrame

	def selectActive(self, cursorX = None, cursorY = None): None
	
	def setText(self, s): self._text = s
	def text(self): return self._text

	def textAlign(self): return self._textAlign
	def setTextAlign(self, align): self._textAlign = align
	
	def bgColor(self): return self._bgColor
	def setBgColor(self, color): self._bgColor = color
	
	def hMargin(self): return self._hMargin
	def setHMargin(self, hm): self._hMargin = hm
	
	def vMargin(self): return self._vMargin
	def setVMargin(self, vm): self._vMargin = vm
	
	def boundingBoxOfText(self):
		return BoundingBox(self.x0()+self.hMargin(), self.y0()+self.vMargin(), self.x1()-self.hMargin(), self.y1()-self.vMargin())

	def resize(self, w, h):
		x0 = self.cx() - w/2
		x1 = self.cx() + w/2
		y0 = self.cy() - h/2
		y1 = self.cy() + h/2
		# try to compensate rounding errors
		# x0 = x0 + (x1-x0+1 - w)
		# y0 = y0 + (y1-y0+1 - h)
		self.setCoords(x0, y0, x1, y1)
		self.updateGeometry()
		
	def moveCenter(self, cx, cy):
		dx = cx - self.cx()
		dy = cy - self.cy()
		self.setCoords(self.x0() + dx, self.y0() + dy, self.x1() + dx, self.y1() + dy)
		self.updateGeometry()
	
	def unlink(self):
		""" see Node class for description """
		None

	def node(self): return self._node
	def setNode(self, node): self._node = node

	def doCreateSelectionFrame(self): self._selectionFrame = SelectionFrame(self)
	def doDestroySelectionFrame(self): self._selectionFrame = None
	def selectionFrame(self): return self._selectionFrame

	def setPoints(self, pa): None
	def drawTo(self, p): None
	def containsPoint(self, x, y): None
	def intersectionWithLineSegment(self, ls): None
	def copy(self): None
	def transform(self, cm): None

	def updateGeometry(self):
		""" Recalculate the shape geometry data, when
		    the shapes bounding box is transformed.
		    For efficiency reason this function should
		    be split off (see below)."""
		None

	"""def setCoords(self, x0, y0, x1, y1):
		BoundingBox.setCoords(self, x0, y0, x1, y1)
		if BoundingBox.valid(self): self.updateGeometry()"""

	def beginInlineTextEdit(self): 
		self._inlineEditMode = True
		
	def endInlineTextEdit(self): 
		self._inlineEditMode = False
	
	def inlineEditMode(self): return self._inlineEditMode

	def updateTransformX(self, fx, dx):
		BoundingBox.updateTransformX(self, fx, dx)
		self.updateGeometry()

	def updateTransformY(self, fy, dy):
		BoundingBox.updateTransformY(self, fy, dy)
		self.updateGeometry()

	def updateTransform(self, fx, fy, dx, dy):
		BoundingBox.updateTransform(self, fx, fy, dx, dy)
		self.updateGeometry()

	def abortTransform(self):
		BoundingBox.abortTransform(self)
		self.updateGeometry()

	def writeXml(self, sink):
		sink.write("<"+self.typeName()+">\n")
		sink.stepDown()
		sink.write("<text>%s</text>\n" % relaceXmlSymbols(str(self.text())))
		sink.write("<bgColor>\n")
		sink.stepDown()
		c = self.bgColor()
		sink.write("<red>%d</red>\n" % c.red())
		sink.write("<green>%d</green>\n" % c.green())
		sink.write("<blue>%d</blue>\n" % c.blue())
		sink.stepUp()
		sink.write("</bgColor>\n")
		sink.write("<textAlign>%d</textAlign>\n" % self.textAlign())
		sink.write("<hMargin>%d</hMargin>\n" % self.hMargin())
		sink.write("<vMargin>%d</vMargin>\n" % self.vMargin())
		BoundingBox.writeXml(self, sink)
		sink.stepUp()
		sink.write("</"+self.typeName()+">\n")

	def readXml(self, source, path):
		path.append(self)
		source.get("<"+self.typeName()+">")
		source.get("<text>")
		if source.lookAhead() != tag("</text>"):
			self._text = source.get().value()
		else:
			self._text = ""
		source.get("</text>")
		source.get("<bgColor>")
		source.get("<red>")
		r = int(source.get().value())
		source.get("</red>")
		source.get("<green>")
		g = int(source.get().value())
		source.get("</green>")
		source.get("<blue>")
		b = int(source.get().value())
		source.get("</blue>")
		source.get("</bgColor>")
		self.setBgColor(QColor(r, g, b))
		source.get("<textAlign>")
		self.setTextAlign(int(source.get().value()))
		source.get("</textAlign>")
		source.get("<hMargin>")
		self.setHMargin(int(source.get().value()))
		source.get("</hMargin>")
		source.get("<vMargin>")
		self.setVMargin(int(source.get().value()))
		source.get("</vMargin>")
		BoundingBox.readXml(self, source, path)
		self.updateGeometry()
		source.get("</"+self.typeName()+">")
		path.pop()
