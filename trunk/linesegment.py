#!/usr/bin/python
# -*- coding: UTF-8 -*-

from qt import *
from numarray import *
from numarray.linear_algebra import *
from numarray_accel import *

class LineSegment:
	""" directed 2D line segment from p0 to p1 """

	def __init__(self, p0, p1):
		self._p0 = p0
		self._p1 = p1

	def intersectionWithLineSegment(self, l2):
		""" calculate the intersection of a two line segment
		    or return None if they do not intersect """
		(o1, a1) = (self._p0, self._p1 - self._p0)
		(o2, a2) = (l2._p0, l2._p1 - l2._p0)
		cm = array([[a1[0], -a2[0]],
		            [a1[1], -a2[1]]])
		d0 = determinant(cm)
		if d0 == 0: return None
		s = matrixmultiply(inverse(cm, d0), o2 - o1)
		if not (0 <= s[0] <= 1 and 0 <= s[1] <= 1): return None
		return s[0] * a1 + o1

	def intersectionWithLine(self, l2):
		""" calculate the intersection of a two line segment
		    or return None if they do not intersect """
		(o1, a1) = (self._p0, self._p1 - self._p0)
		(o2, a2) = (l2._p0, l2._p1 - l2._p0)
		cm = array([[a1[0], -a2[0]],
		           [a1[1], -a2[1]]])
		d0 = determinant(cm)
		if d0 == 0: return None
		s = matrixmultiply(inverse(cm, d0), o2 - o1)
		if not (0 <= s[0] <= 1): return None
		return s[0] * a1 + o1

	def p0(self): return self._p0
	def p1(self): return self._p1

	def setP0(self, p0): self._p0 = p0
	def setP1(self, p1): self._p1 = p1

	def drawTo(self, p):
		p.drawLine(self._p0[0], self._p0[1], self._p1[0], self._p1[1])
