#!/usr/bin/python
# -*- coding: UTF-8 -*-

from numarray import *
from numarray.linear_algebra import *
from numarray_accel import *

class Line:
	""" Directed line of 2D space with goes through p0 and p1.
	    The line is directed from p0 to p1.
	    From this perspective a left and a right side of
	    the line is defined.
	"""

	def __init__(self, p0, p1):
		self._p0 = p0
		self._p1 = p1

	def p0(self): return self._p0
	def p1(self): return self._p1

	def setP0(self, p0): self._p0 = p0
	def setP1(self, p1): self._p1 = p1

	def copy(self):
		return Line(self._p0, self._p1)

	def moveLeft(self, s):
		""" Move the line left by s steps (in global raster units).
		"""
		a = self._p1 - self._p0
		nl = array([-a[1], a[0]])
		d = sqrt(a[0] * a[0] + a[1] * a[1])
		nl = s/d*nl
		self._p0 = self._p0 + nl
		self._p1 = self._p1 + nl

	def moveRight(self, s):
		""" Move the line right by s steps (in global raster units).
		"""
		a = self._p1 - self._p0
		nr = array([a[1], -a[0]])
		d = sqrt(a[0] * a[0] + a[1] * a[1])
		nr = s/d*nr
		self._p0 = self._p0 + nr
		self._p1 = self._p1 + nr

	def intersectionWithLine(self, l2):
		""" calculate the intersection of a two lines
			or return None if they do not intersect """
		(o1, a1) = (self._p0, self._p1 - self._p0)
		(o2, a2) = (l2._p0, l2._p1 - l2._p0)
		cm = array([[a1[0], -a2[0]],
		            [a1[1], -a2[1]]])
		d0 = determinant(cm)
		if d0 == 0: return None
		s = matrixmultiply(inverse(cm, d0), o2 - o1)
		return s[0] * a1 + o1

	def intersectionWithLineSegment(self, l2):
		""" calculate the intersection with a line segment
			or return None if intersection is an empty set """
		(o1, a1) = (self._p0, self._p1 - self._p0)
		(o2, a2) = (l2._p0, l2._p1 - l2._p0)
		cm = array([[a1[0], -a2[0]],
		            [a1[1], -a2[1]]])
		d0 = determinant(cm)
		if d0 == 0: return None
		s = matrixmultiply(inverse(cm, d0), o2 - o1)
		if not 0 <= s[1] <= 1: return None
		return s[0] * a1 + o1

