#!/usr/bin/python
# -*- coding: UTF-8 -*-

from numarray import *
from linesegment import *

class CoordinateSystem:

	def __init__(self, u, v, o):
		self._u = u
		self._v = v
		self._o = o

	def u(self): return self._u
	def v(self): return self._v
	def o(self): return self._o

	def setU(self, u): self._u = u
	def setV(self, v): self._v = v
	def setO(self, o): self._o = o

	def norm(self):
		d0 = sqrt(self._u[0] * self._u[0] + self._u[1] * self._u[1])
		d1 = sqrt(self._v[0] * self._v[0] + self._v[1] * self._v[1])
		if d0 == 0 or d1 == 0: return
		self._u = self._u / d0
		self._v = self._v / d1

	def base(self):
		""" returns the system's defining matrix """
		cm = array(shape=(3,3), type=Float64)
		cm[0:2,0] = self._u
		cm[0:2,1] = self._v
		cm[0:2,2] = self._o
		cm[2] = array([0, 0, 1])
		return cm

	def drawTo(self, p):
		p.setPen(Qt.black)
		p0 = self._o - 10 * self._u
		p1 = self._o + 10 * self._u
		q0 = self._o - 10 * self._v
		q1 = self._o + 10 * self._v
		a0 = LineSegment(p0, p1)
		a1 = LineSegment(q0, q1)
		a0.drawTo(p)
		a1.drawTo(p)

