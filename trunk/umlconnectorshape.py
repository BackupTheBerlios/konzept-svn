# -*- coding: UTF-8 -*-

from qt import *
from numarray import *
from math import *

from connectorshape import *
from xmlfactory import *
from xmltokensource import *
from indentsink import *
from uml import *

class UmlConnectorShape(ConnectorShape):
	def __init__(self, type = None, p0 = None, p1 = None):
		ConnectorShape.__init__(self, p0, p1)
		
		self.setType(type)
		
		# geometry helper variables
		self._q0 = None
		self._q1 = None
		self._q2 = None
		self._q3 = None
		self._toShort = False
		
		self._activeWidth = 12
		
		self._x0 = 0
		self._x1 = None
		self._y0 = -self._activeWidth/2
		self._y1 = self._activeWidth/2
		
		self.updateGeometry()
		
	def staticTypeName(): return "UmlConnectorShape"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return UmlConnectorShape()
	newInstance = staticmethod(newInstance)
	
	def typeName(self): return UmlConnectorShape.staticTypeName()
	
	def setLabel0(self, label):
		if self._label0 != None: self._label0 = label
	
	def setLabel1(self, label):
		if self._label1 != None: self._label1 = label
	
	def label0(self): return self._label0
	def label1(self): return self._label1
	
	def updateGeometry(self):
		ConnectorShape.updateGeometry(self)
		
		if self._p0 == None or self._p1 == None: return
		
		q = self._p1 - self._p0
		dq = sqrt(q[0] * q[0] + q[1] * q[1])
		if dq <= self._headLength:
			self._toShort = True
			return
		self._toShort = False
		s = (dq - self._headLength) / dq
		self._q0 = s * q + self._p0
		n = ((self._headWidth/2) / dq) * array([q[1], -q[0]])
		self._q1 = self._q0 + n
		self._q2 = self._q0 - n
		if self._type in [Uml.aggregation, Uml.composition]:
			n2 = ((self._headLength/2) / dq) * q
			self._q1 = self._q1 + n2
			self._q2 = self._q2 + n2
		self._x1 = dq
		
		p0 = self._p0
		p1 = self._p1
		
		dx = p1[0] - p0[0]
		dy = p1[1] - p0[1]
		
		if dx == 0: 
			if dy < 0: self._alpha = 90
			else: self._alpha = -90
		else:
			self._alpha = 180*atan(dy/dx)/pi
		
		if dx > 0:
			self._rightSide = True
		else:
			self._rightSide = False
		
		self._q3 = self._p0 + q/2

		# print self._alpha
	
	def drawTo(self, p):
		if self._p0 == None or self._p1 == None: return
		if self._toShort: return
		
		# if paint events occurs before updateGeometry!
		if self._q0 == None: return
		
		pen = QPen()
		pen.setColor(Qt.black)
		pen.setWidth(1)
		p.setPen(pen)
		
		if self._type == Uml.aggregation:
			p.drawLine(self._p0[0], self._p0[1], self._q0[0], self._q0[1])
			a = QPointArray(5)
			a.setPoint(0, self._q0[0], self._q0[1])
			a.setPoint(1, self._q1[0], self._q1[1])
			a.setPoint(2, self._p1[0], self._p1[1])
			a.setPoint(3, self._q2[0], self._q2[1])
			a.setPoint(4, self._q0[0], self._q0[1])
			p.drawPolyline(a)
		elif self._type == Uml.composition:
			p.drawLine(self._p0[0], self._p0[1], self._q0[0], self._q0[1])
			a = QPointArray(4)
			a.setPoint(0, self._q0[0], self._q0[1])
			a.setPoint(1, self._q1[0], self._q1[1])
			a.setPoint(2, self._p1[0], self._p1[1])
			a.setPoint(3, self._q2[0], self._q2[1])
			p.setBrush(QBrush(Qt.black))
			p.drawPolygon(a)
		elif self._type == Uml.generalization:
			p.drawLine(self._p0[0], self._p0[1], self._q0[0], self._q0[1])
			p.drawLine(self._q1[0], self._q1[1], self._q2[0], self._q2[1])
			p.drawLine(self._q1[0], self._q1[1], self._p1[0], self._p1[1])
			p.drawLine(self._q2[0], self._q2[1], self._p1[0], self._p1[1])
		elif self._type == Uml.implements:
			p.drawLine(self._q1[0], self._q1[1], self._q2[0], self._q2[1])
			p.drawLine(self._q1[0], self._q1[1], self._p1[0], self._p1[1])
			p.drawLine(self._q2[0], self._q2[1], self._p1[0], self._p1[1])
			pen = QPen(Qt.black)
			pen.setStyle(Qt.DashLine)
			pen.setWidth(1)
			p.setPen(pen)
			p.drawLine(self._p0[0], self._p0[1], self._q0[0], self._q0[1])
		elif self._type == Uml.dependency:
			p.drawLine(self._q1[0], self._q1[1], self._p1[0], self._p1[1])
			p.drawLine(self._q2[0], self._q2[1], self._p1[0], self._p1[1])
			pen = QPen(Qt.black)
			pen.setStyle(Qt.DashLine)
			pen.setWidth(1)
			p.setPen(pen)
			p.drawLine(self._p0[0], self._p0[1], self._p1[0], self._p1[1])
		elif self._type == Uml.association:
			p.drawLine(self._p0[0], self._p0[1], self._p1[0], self._p1[1])
			p.drawLine(self._q1[0], self._q1[1], self._p1[0], self._p1[1])
			p.drawLine(self._q2[0], self._q2[1], self._p1[0], self._p1[1])
		elif self._type == Uml.relation:
			p.drawLine(self._p0[0], self._p0[1], self._p1[0], self._p1[1])
			
		p.save()
		font = QFont("Sans")
		font.setPixelSize(8)
		p.setFont(font)
		if self._type in [Uml.association, Uml.aggregation, Uml.composition]:
			p.translate(self._q0[0], self._q0[1])
			p.rotate(self._alpha)
			if self._rightSide:
				p.drawText(-(p.fontMetrics().width(self.label1())+1), -3, self.label1())
			else:
				p.drawText(1, -3, self.label1())
		elif self._type in [Uml.generalization, Uml.dependency, Uml.implements]:
			p.translate(self._q3[0], self._q3[1])
			p.rotate(self._alpha)
			if self._rightSide:
				p.drawText(-(p.fontMetrics().width(self.label0())/2), -3, self.label0())
			else:
				p.drawText(-(p.fontMetrics().width(self.label0())/2), -3, self.label0())
		elif self._type == Uml.relation:
			p.translate(self._q0[0], self._q0[1])
			p.rotate(self._alpha)
			if self._rightSide:
				p.drawText(-(p.fontMetrics().width(self.label0())+2), -3, self.label0())
			else:
				p.drawText(2, -3, self.label0())
			p.restore()
			p.save()
			font = QFont("Sans")
			font.setPixelSize(8)
			p.setFont(font)
			p.translate(self._p0[0], self._p0[1])
			p.rotate(self._alpha)
			if self._rightSide:
				p.drawText(2, -3, self.label1())
			else:
				p.drawText(-(p.fontMetrics().width(self.label1())+2), -3, self.label1())
		p.restore()

	def type(self): return self._type
	
	def setType(self, type):
		self._type = type
		
		if type in [Uml.generalization, Uml.implements]:
			self._headLength = 10.0
			self._headWidth = 10.0
		elif type in [Uml.dependency, Uml.association]:
			self._headLength = 10.0
			self._headWidth = 6.0
		elif type in [Uml.aggregation, Uml.composition]:
			self._headLength = 16.0
			self._headWidth = 10.0
			self._label0 = None
			self._label1 = ""
		elif type == Uml.relation:
			self._headLength = 0
			self._headWidth = 0
			self._label0 = ""
			self._label1 = ""
		elif type == None:
			self._headLength = 0
			self._headWidth = 0
			self._label0 = ""
			self._label1 = ""

		if type in [Uml.aggregation, Uml.composition, Uml.association]:
			self._label0 = None
			self._label1 = ""
		elif type in [Uml.generalization, Uml.implements, Uml.dependency]:
			self._label0 = ""
			self._label1 = None
		elif type == Uml.relation:
			self._label0 = ""
			self._label1 = ""
		elif type == None:
			self._label0 = None
			self._label1 = None
			
	def copy(self):
		shape = UmlConnectorShape(self.type(), self.p0(), self.p1())
		shape.setLabel0(self.label0())
		shape.setLabel1(self.label1())
		return shape

	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		sink.stepDown()
		sink.write("<type>%s</type>\n" % self.type())
		if self.label0() != None:
			sink.write("<label0>%s</label0>\n" % relaceXmlSymbols(self.label0()))
		if self.label1() != None:
			sink.write("<label1>%s</label1>\n" % relaceXmlSymbols(self.label1()))
		sink.stepUp()
		sink.write("</%s>\n" % self.typeName())

	def readXml(self, source, path):
		path.append(self)
		source.get("<%s>" % self.typeName())
		source.get("<type>")
		self.setType(int(source.get().value()))
		source.get("</type>")
		if source.lookAhead() == tag("<label0>"):
			source.get("<label0>")
			if source.lookAhead() != tag("</label0>"):
				self.setLabel0(source.get().value())
			source.get("</label0>")
		if source.lookAhead() == tag("<label1>"):
			source.get("<label1>")
			if source.lookAhead() != tag("</label1>"):
				self.setLabel1(source.get().value())
			source.get("</label1>")
		source.get("</%s>" % self.typeName())
		path.pop()

XmlFactory.instance(ConnectorShape).registerType(UmlConnectorShape)
