# -*- coding: UTF-8 -*-

from qt import *
from mousecursors import *
from selectionframe import *
from math import *

class TransformFrame(SelectionFrame):

	# transformation types
	move = 0
	moveX0 = 1
	moveX1 = 2
	moveY0 = 3
	moveY1 = 4
	moveX0Y0 = 5
	moveX0Y1 = 6
	moveX1Y0 = 7
	moveX1Y1 = 8

	# type index to cursor shape mapping
	cursorShapes = [
		mouseCursors.sizeAllCursor(),
		mouseCursors.sizeHorCursor(),
		mouseCursors.sizeHorCursor(),
		mouseCursors.sizeVerCursor(),
		mouseCursors.sizeVerCursor(),
		mouseCursors.sizeFDiagCursor(),
		mouseCursors.sizeBDiagCursor(),
		mouseCursors.sizeBDiagCursor(),
		mouseCursors.sizeFDiagCursor()
	] 
	
	def __init__(self, boundingBox):
		SelectionFrame.__init__(self, boundingBox)

		self._transformType = None
		self._cursorShape = None
		self._keepAspect = False

		# transformation base point
		self._tx0 = None
		self._ty0 = None

		self._keepAspect = False

	def coordsObject(self):
		return self._boundingBox

	def getTransformType(self, x, y):
		if self.x0Bar().containsPoint(x, y):
			type = TransformFrame.moveX0
		elif self.x1Bar().containsPoint(x, y):
			type = TransformFrame.moveX1
		elif self.y0Bar().containsPoint(x, y):
			type = TransformFrame.moveY0
		elif self.y1Bar().containsPoint(x, y):
			type = TransformFrame.moveY1
		elif self.x0Y0Handle().containsPoint(x, y):
			type = TransformFrame.moveX0Y0
		elif self.x0Y1Handle().containsPoint(x, y):
			type = TransformFrame.moveX0Y1
		elif self.x1Y0Handle().containsPoint(x, y):
			type = TransformFrame.moveX1Y0
		elif self.x1Y1Handle().containsPoint(x, y):
			type = TransformFrame.moveX1Y1
		else:
			type = TransformFrame.move
		return type

	def beginTransform(self, x, y, type = None):
		(self._tx0, self._ty0) = (x, y) # store transformation base point
		(self._dx2, self._dy2) = (0, 0) # last deviation from transform base point
		if type == None: type = self.getTransformType(x, y)
		self._transformType = type
		self._boundingBox.beginTransform()
		return TransformFrame.cursorShapes[type]
	
	def endTransform(self):
		self._boundingBox.endTransform()

	def abortTransform(self):
		self._boundingBox.abortTransform()

	def keepAspect(self):
		return self._keepAspect

	def setKeepAspect(self, keepAspect):
		self._keepAspect = keepAspect

	def getCursorShapeByMode(self):
		if self._cursorShape != None: return self._cursorShape
		return mouseCursors.pointingHandCursor()

	def keyPressEvent(self, event):
		# if event.key() ==
		return

	def mouseMoveEvent(self, cursorX, cursorY):
		bb = self._boundingBox

		dx = cursorX - self._tx0
		dy = cursorY - self._ty0

		# absolute transform speed
		vx = abs(dx - self._dx2) 
		vy = abs(dy - self._dy2)
		
		self._dx2 = dx
		self._dy2 = dy
		
		if self._transformType == TransformFrame.moveX0:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0() + dx, bb.orig().x1())
			(y0, y1) = (bb.orig().y0()     , bb.orig().y1())
			x0 = bb.clampX0(x0, x1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
			# if self._keepAspect:
			#	fy = fx
		elif self._transformType == TransformFrame.moveY0:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0()     , bb.orig().x1())
			(y0, y1) = (bb.orig().y0() + dy, bb.orig().y1())
			y0 = bb.clampY0(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
			# if self._keepAspect:
			#	fx = fy
		elif self._transformType == TransformFrame.moveX1:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0(), bb.orig().x1() + dx)
			(y0, y1) = (bb.orig().y0(), bb.orig().y1())
			x1 = bb.clampX1(x0, x1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
			# if self._keepAspect:
			#	fy = fx
		elif self._transformType == TransformFrame.moveY1:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0(), bb.orig().x1())
			(y0, y1) = (bb.orig().y0(), bb.orig().y1() + dy)
			y1 = bb.clampY1(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
			# if self._keepAspect:
			#	fx = fy
		elif self._transformType == TransformFrame.moveX0Y0:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0() + dx, bb.orig().x1())
			(y0, y1) = (bb.orig().y0() + dy, bb.orig().y1())
			x0 = bb.clampX0(x0, x1)
			y0 = bb.clampY0(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
		elif self._transformType == TransformFrame.moveX0Y1:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0() + dx, bb.orig().x1())
			(y0, y1) = (bb.orig().y0()     , bb.orig().y1() + dy)
			x0 = bb.clampY0(x0, x1)
			y1 = bb.clampY1(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
		elif self._transformType == TransformFrame.moveX1Y0:
			if self._keepAspect: return
			(x0, x1) = (bb.orig().x0()     , bb.orig().x1() + dx)
			(y0, y1) = (bb.orig().y0() + dy, bb.orig().y1())
			x1 = bb.clampX1(x0, x1)
			y0 = bb.clampY0(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
		elif self._transformType == TransformFrame.moveX1Y1:
			(x0, x1) = (bb.orig().x0(), bb.orig().x1() + dx)
			(y0, y1) = (bb.orig().y0(), bb.orig().y1() + dy)
			x1 = bb.clampX1(x0, x1)
			y1 = bb.clampY1(y0, y1)
			(fx, fy, dx, dy) = self.getTransformParams(bb, x0, y0, x1, y1)
			# fx = float(x1 - x0 + 1) / bb.orig().width()
			# fy = float(y1 - y0 + 1) / bb.orig().height()
			# (dx, dy) = (0, 0)
			if self._keepAspect:
				fx = fy = max(fx, fy)
		elif self._transformType == TransformFrame.move:
			if self._keepAspect:
				if vx > vy: dy = 0
				else: dx = 0
			(fx, fy) = (1, 1)

		wouldX = bb.wouldTransformX(fx, dx)
		wouldY = bb.wouldTransformY(fy, dy)
		#print "wouldX, wouldY = ", wouldX, wouldY
		#print "fx,fy,dx,dy = ", fx, fy, dx, dy
		if wouldX and wouldY:
			bb.updateTransform(fx, fy, dx, dy)
		elif wouldX:
			bb.updateTransformX(fx, dx)
		elif wouldY:
			bb.updateTransformY(fy, dy)

	def getTransformParams(self, bb, x0, y0, x1, y1):
		o = bb.orig()
		fx = float((x1 - x0)) / (o.width() - 1)
		fy = float((y1 - y0)) / (o.height() - 1)
		dx = x0 - o.x0()
		dy = y0 - o.y0()
		return (fx, fy, dx, dy)

	"""def drawTo(self, p):
		SelectionFrame.drawTo(self, p)
		p.setPen(QPen(Qt.black))
		p.setBrush(QBrush(Qt.white))
		l = [self.x0Y0Handle(), self.x1Y0Handle(), self.x0Y1Handle(), self.x1Y1Handle()]
		for bb in l:
			p.drawRect(bb.x0(), bb.y0(), bb.width(), bb.height())"""