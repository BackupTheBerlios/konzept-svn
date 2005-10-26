# -*- coding: UTF-8 -*-

from qt import *
from re import *
# from nodeshape import *

class InlineEditor(QTextEdit):
	""" An InlineEditor allows to edit decriptive text
	    carried by connectors, nodes and other graphical elements. """

	def __init__(self, parent):
		QTextEdit.__init__(self, parent)
		self._graphEdit = parent
		self.hide()
		#self.setGeometry(self.x0()+1, self.y0()+1, self.width()-2, self.height()-2)
		font = QFont("Sans")
		font.setPixelSize(10)
		self.setFont(font)
		#self.setWrapPolicy(0)
		self.setWordWrap(QTextEdit.NoWrap)
		self.setFrameShape(QTextEdit.NoFrame)
		self.setHScrollBarMode(QTextEdit.AlwaysOff)
		self.setVScrollBarMode(QTextEdit.AlwaysOff)
		self.setTextFormat(Qt.PlainText)
		self.connect(self, SIGNAL("textChanged()"), self.textChanged)

	def graphEdit(self): return self._graphEdit
	def shape(self): return self._shape
	
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self._graphEdit.endInlineTextEdit()
		else:
			QTextEdit.keyPressEvent(self, event)

	def textChanged(self):
		if self.shape() == None: return
		self.shape().setText(self.text().ascii())
		self.shape().optimizeSize()
		bbox = self.shape().boundingBoxOfText()
		if not bbox.valid(): return
		(x0, y0) = (-self.graphEdit().pageX0(), -self.graphEdit().pageY0())
		self.setGeometry(x0 + bbox.x0()-2, y0 + bbox.y0()-1, bbox.width()+6, bbox.height()+4)
		self.graphEdit().updateContents()
		
	def prepareText(self, t):
		t = sub("&lt;", "<", t)
		t = sub("&gt;", ">", t)
		t = sub("&nbsp;", " ", t)
		t = sub("<br>", "\n", t)
		return t
		
	def finishText(self, t):
		t = sub("<", "&lt;", t)
		t = sub(">", "&gt;", t)
		t = sub("&lt;[bB]&gt;", "<b>", t)
		t = sub("&lt;[iI]&gt;", "<i>", t)
		t = sub("&lt;[uU]&gt;", "<u>", t)
		t = sub("&lt;center&gt;", "<center>", t)
		t = sub("&lt;CENTER&gt;", "<center>", t)
		t = sub("&lt;/[bB]&gt;", "</b>", t)
		t = sub("&lt;/[iI]&gt;", "</i>", t)
		t = sub("&lt;/[uU]&gt;", "</u>", t)
		t = sub("&lt;/center&gt;", "</center>", t)
		t = sub("&lt;/CENTER&gt;", "</center>", t)
		t = sub(" ", "&nbsp;", t)
		t = sub("\n", "<br>", t)
		return t

	def beginEditing(self, shape):
		self._shape = shape
		self._shape.selectActive(self.graphEdit().cursorX(), self.graphEdit().cursorY())
		self._shape.beginInlineTextEdit()
		bbox = self._shape.boundingBoxOfText()
		(x0, y0) = (-self.graphEdit().pageX0(), -self.graphEdit().pageY0())
		self.setMargin(0)
		self.setLineWidth(0)
		self.setMidLineWidth(0)
		self.setGeometry(x0 + bbox.x0()-2, y0 + bbox.y0()-1, bbox.width()+6, bbox.height()+4)
		self.setPaper(QBrush(self._shape.bgColor()))
		# self.setPaper(QBrush(Qt.red))
		self.setText(self.prepareText(self._shape.text()))
		self.setFocus()
		self.show()

	def endEditing(self):
		self.hide()
		self.clearFocus()
		self._shape.setText(self.finishText(str(self.text().ascii())))
		self._shape.endInlineTextEdit()
		self.shape().optimizeSize()


