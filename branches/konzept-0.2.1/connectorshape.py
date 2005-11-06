#!/usr/bin/python
# -*- coding: UTF-8 -*-

from numarray import *
from numarray.linear_algebra import *
from numarray_accel import *
from coordinatesystem import *
from boundingbox import *
from connectorselectionframe import *

class ConnectorShape:
	def __init__(self, p0 = None, p1 = None):
		self._headSize = 14
		(self._p0, self._p1) = (p0, p1)

		# bounding box description to implement containsPoint
		# see p. 82 of big script book
		self._coordinateSystem = None
		self._x0 = None
		self._x1 = None
		self._y0 = None
		self._y1 = None

		self._selectionFrame = None

	def typeName(self): return "ConnectorShape"
	
	def p0(self): return self._p0
	def p1(self): return self._p1

	def setP0(self, p0): self._p0 = p0
	def setP1(self, p1): self._p1 = p1
	def setP0P1(self, p0, p1): (self._p0, self._p1) = (p0, p1)

	def doCreateSelectionFrame(self): self._selectionFrame = ConnectorSelectionFrame(self)
	def doDestroySelectionFrame(self): self._selectionFrame = None
	def selectionFrame(self): return self._selectionFrame

	def updateGeometry(self):
		if self._p0 == None or self._p1 == None: return

		o = self._p0
		u = self._p1 - self._p0
		v = array([-u[1], u[0]])
		self._coordinateSystem = CoordinateSystem(u,v,o)
		self._coordinateSystem.norm()

	def drawTo(self, p):
		None
		""" if self._p0 == None or self._p1 == None: return
		self._coordinateSystem.drawTo(p) """

	def containsPoint(self, x, y):
		if self._x0 == None or self._y0 == None or self._x1 == None or self._y1 == None \
		or self._coordinateSystem == None:
			return False

		# p. 82 of big script book
		base = self._coordinateSystem.base()
		if determinant(base) == 0: return

		q = matrixmultiply(inverse(base), array([x, y, 1]))
		(x, y) = (q[0], q[1])

		bbox = BoundingBox(self._x0, self._y0, self._x1, self._y1)
		return bbox.containsPoint(x,y)

	def copy(self): return None

	def writeXml(self, sink):
		sink.write("<"+self.typeName()+">\n")
		sink.write("</"+self.typeName()+">\n")

	def readXml(self, source, path):
		source.get("<"+self.typeName()+">")
		source.get("</"+self.typeName()+">")
