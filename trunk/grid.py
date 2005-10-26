# -*- coding: utf-8 -*-

from qt import *
from xmlfactory import *

class Grid:
	defaultRasterSize_mm = 10

	def __init__(self, rs_mm = defaultRasterSize_mm):
		self.setRasterSize_mm(rs_mm)
		self.setColor(QColor(230, 230, 230))

	def staticTypeName(): return "Grid"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return Grid()
	newInstance = staticmethod(newInstance)

	def typeName(self): return Grid.staticTypeName()

	def setRasterSize_mm(self, rs_mm): self._rasterSize = rs_mm*72.27/25.4
	def rasterSize_mm(self): return self._rasterSize*25.4/72.27
	def setRasterSize(self, rs): self._rasterSize = rs
	def rasterSize(self): return self._rasterSize
	
	def setColor(self, c): self._color = c
	def color(self): return self._color
	
	def nearest(self, x, y):
		rs = self.rasterSize()
		(dx, dy) = (x % rs, y % rs)
		if dx > rs/2: dx = rs - dx
		else: dx = -dx
		if dy > rs/2: dy = rs - dy
		else: dy = -dy
		return (round(x + dx), round(y + dy))

	def drawTo(self, p, w, h):
		p.save()
		pen = QPen()
		pen.setColor(self.color())
		pen.setWidth(0)
		p.setPen(pen)
		dx = self.rasterSize()
		x = dx
		while x < w:
			p.drawLine(x, 1, x, h-2)
			x = x + dx
		x = dx
		while x < h:
			p.drawLine(1, x, w-2, x)
			x = x + dx
		p.restore()
		
	def writeXml(self, sink):
		sink.write("<Grid>\n")
		sink.stepDown()
		sink.write("<rasterSize>%d</rasterSize>\n" % self.rasterSize_mm())
		sink.stepUp()
		sink.write("</Grid>\n")

	def readXml(self, source, path = []):
		path.append(self)
		source.get("<Grid>")
		source.get("<rasterSize>")
		self.setRasterSize_mm(int(source.get().value()))
		source.get("</rasterSize>")
		source.get("</Grid>")
		path.pop()

XmlFactory.instance(Grid).registerType(Grid)
