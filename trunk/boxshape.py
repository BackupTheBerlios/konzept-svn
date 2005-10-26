# -*- coding: UTF-8 -*-

from xmlfactory import *
from rectangleshape import *
from boundingbox import *
from qt import *

class BoxShape(RectangleShape):
	def __init__(self, x0 = None, y0 = None, x1 = None, y1 = None):
		RectangleShape.__init__(self, x0, y0, x1, y1)
		self.setTextAlign(Qt.AlignLeft | Qt.AlignTop)
		self.setBgColor(QColor(239,247,255))
		self.setHMargin(5)
		self.setVMargin(4)

	def staticTypeName(): return "BoxShape"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return BoxShape()
	newInstance = staticmethod(newInstance)

	def typeName(self): return BoxShape.staticTypeName()

	def drawTo(self, p):
		pen = QPen()
		pen.setColor(Qt.black)
		pen.setWidth(1)
		p.setPen(pen)
		RectangleShape.drawTo(self, p)
		# p.setPen(Qt.black)
		bbox = self.boundingBoxOfText()
		font = QFont("Sans")
		font.setPixelSize(10)
		if not bbox.valid(): return
		if self.inlineEditMode(): return
		r = QRect(bbox.x0(), bbox.y0(), bbox.width(), bbox.height())
		t = QSimpleRichText(self.text(), font) 
		t.setWidth(p, bbox.width())
		#p.drawText(r, self.textAlign(), self.text(), -1, r)
 		space = QFontMetrics(font).height() - QFontMetrics(font).ascent()
		leading = QFontMetrics(font).leading()
		x0 = bbox.x0()
		y0 = bbox.y0()
		if self.textAlign() & Qt.AlignLeft:
			x0 += 1
		elif self.textAlign() & Qt.AlignHCenter:
			x0 += (bbox.width() - t.widthUsed())/2 + 4
		elif self.textAlign() & Qt.AlignRight:
			x0 += bbox.width() - t.widthUsed() + space + 4

		if self.textAlign() & Qt.AlignTop:
			y0 -= space
		elif self.textAlign() & Qt.AlignVCenter:
			y0 += (bbox.height() - t.height() - space + leading)/2
		elif self.textAlign() & Qt.AlignBottom:
			y0 += bbox.height() - t.height()
		
		t.draw(p, x0, y0, QRect(), QColorGroup(), QBrush(self.bgColor()))

	def optimizeSize(self):
		font = QFont("Sans")
		font.setPixelSize(10)
		s = str(self.text())
		if len(s) != 0: 
			if s[-1] == '\n': s += " "
		if self.inlineEditMode() == False:
			t = QSimpleRichText(s, font)
			w = 2 * self._hMargin + t.widthUsed()
			h = 2 * self._vMargin + t.height()
			self.resize(w, h)
		else:
			if s == "": s = " "
			m = QFontMetrics(font).size(0, s)
			w = 2 * self._hMargin + m.width()
			h = 2 * self._vMargin + m.height()
			self.resize(w, h)
		
	def copy(self):
		s2 = BoxShape(self.x0(), self.y0(), self.x1(), self.y1())
		s2.setText(self.text())
		s2.setTextAlign(self.textAlign())
		s2.setBgColor(self.bgColor())
		s2.setHMargin(self.hMargin())
		s2.setVMargin(self.vMargin())
		return s2
	
XmlFactory.instance(NodeShape).registerType(BoxShape)
