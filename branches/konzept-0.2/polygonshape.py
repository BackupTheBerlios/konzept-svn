# -*- coding: UTF-8 -*-

from qt import *
from numarray import *
from numarray.linear_algebra import *
from numarray.linear_algebra.mlab import *
from linesegment import *
from line import *
from nodeshape import *

class PolygonShape(NodeShape):
	""" convex polygonal shape with mathematical
	    negative orientation (orientation of an analog clock)
	"""

	def __init__(self, pa = None):
		NodeShape.__init__(self)
		self._outline = array([])
		if pa != None: self.setPoints(pa)

	def setPoints(self, pa):
		""" set the egde point array to pa """
		self._outline = pa
		self._x0 = min(self._outline[:,0])
		self._x1 = max(self._outline[:,0])
		self._y0 = min(self._outline[:,1])
		self._y1 = max(self._outline[:,1])
		if self.node() != None:
			self.node().updateConnectors()

	def outline(self): return self._outline
	
	def drawTo(self, p):
		if len(self._outline) <= 2: return

		p.setBrush(QBrush(self.bgColor()))
		
		n = len(self._outline)
		qpa = QPointArray(n)
		for i in range(n):
			pi = self._outline[i,0:2]
			qpa.setPoint(i, pi[0], pi[1])

		p.drawPolygon(qpa)

	def containsPoint(self, x, y):
		if len(self._outline) <= 2: return False

		if not ( x >= self.x0() and y >= self.y0() and \
		         x <= self.x1() and y <= self.y1() ):
			return False

		# siehe p25 grosses Skriptbuch

		q = array([x, y])
		n = len(self._outline)

		for i in range(n):
			j = (i + 1) % n
			o = self._outline[i,0:2]
			a = self._outline[j,0:2] - o
			b = array([a[1], -a[0]])
			cm = array([[a[0], b[0]],
			            [a[1], b[1]]])
			if determinant(cm) == 0: continue
			s = matrixmultiply(inverse(cm), q - o)
			if s[1] < 0:
				return False
		return True

	def intersectionWithLineSegment(self, ls):
		""" Returns a list of intersection points of a polygon and a line segment.
		    If there are no intersection points an empty list is return. """
		if len(self._outline) <= 2: return []

		n = len(self._outline)
		intersection = []
		for i in range(n):
			j = (i + 1) % n
			(p0, p1) = (self._outline[i,0:2], self._outline[j,0:2])
			ls2 = LineSegment(p0, p1)
			pi = ls2.intersectionWithLineSegment(ls)
			if pi != None: intersection.append(pi)

		return intersection

	def intersectionWithLine(self, ln):
		""" Returns a list of intersection points of a polygon and a line.
		    If there are no intersection points an empty list is return. """
		if len(self._outline) <= 2: return []

		n = len(self._outline)
		intersection = []
		for i in range(n):
			j = (i + 1) % n
			(p0, p1) = (self._outline[i,0:2], self._outline[j,0:2])
			ls2 = LineSegment(p0, p1)
			pi = ls2.intersectionWithLine(ln)
			if pi != None: intersection.append(pi)

		return intersection

	def copy(self):
		return PolygonShape(self._outline.copy())

	def updateGeometry(self):
		""" noch nicht implementiert, beim beginTransform() die alte
		    Outline speichern und diese jeweils auf die aktuelle skalieren
		    entsprechend fx, fy, dx, dy """
		None

	def transform(self, cm):
		""" Maxtrixmultiply each vector of the outline with cm.
		    cm is a 3x3 matrix. To make the multiplication a valid
		    operation the edge point vectors are expanded by "1". """
		for i in range(len(self._outline)):
			self._outline[i] = matrixmultiply(cm, array([self._outline[i,0], self._outline[i,1], 1]))[0:2]
		self._x0 = min(self._outline[:,0])
		self._x1 = max(self._outline[:,0])
		self._y0 = min(self._outline[:,1])
		self._y1 = max(self._outline[:,1])
		if self.node() != None:
			self.node().updateConnectors()

	def translate(self, dx, dy):
		cm = array([[1, 0, dx],
		            [0, 1, dy],
		            [0, 0, 1]])
		self.transform(cm)
	
	""" def minPointY(self):

	def maxPointY(self):

	def minPointX(self):

	def maxPointX(self): """
