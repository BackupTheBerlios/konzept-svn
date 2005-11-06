# -*- coding: utf-8 -*-

from qt import *
from xmltokensource import *
from indentsink import *

class PageFormat:
	def __init__(self, name = None, width = None, height = None, qFormat = None):
		self._name = name
		self._width = width
		self._height = height
		self._qFormat = qFormat
	
	def name(self): return self._name
	def width(self): return self._width
	def height(self): return self._height
	def qFormat(self): return self._qFormat
	
class PageFormatRegistry:
	def __init__(self):
		self._formats = []
		
	def __getitem__(self, index): return self._formats[index]
	def count(self): return len(self._formats)
	def register(self, fmt): self._formats.append(fmt)
	
	def stringList(self):
		l = QStringList()
		for f in self._formats:
			s = "%s - %d x %d mm" % (f.name(), f.width(), f.height())
			l.append(s)
		return l
	
	def getIndex(self, fmt):
		for i in range(0, len(self._formats)):
			if self._formats[i].name() == fmt.name(): return i
		return None

pageFormatRegistry = PageFormatRegistry()

A4 = PageFormat("A4", 210, 297, QPrinter.A4)

pfr = pageFormatRegistry
pfr.register(PageFormat("A0", 841, 1189, QPrinter.A0))
pfr.register(PageFormat("A1", 594, 841, QPrinter.A1))
pfr.register(PageFormat("A2", 420, 594, QPrinter.A2))
pfr.register(PageFormat("A3", 297, 420, QPrinter.A3))
pfr.register(A4)
pfr.register(PageFormat("A5", 148, 210, QPrinter.A5))
pfr.register(PageFormat("Legal", 216, 356, QPrinter.Legal))
pfr.register(PageFormat("Letter", 216, 279, QPrinter.Letter))

def mm(pt): return int(pt*25.4/72.27)

pfr.register(PageFormat("Slide (640x480 pt)", mm(480), mm(640), QPrinter.Letter))
pfr.register(PageFormat("Slide (800x600 pt)", mm(600), mm(800), QPrinter.Letter))
pfr.register(PageFormat("Slide (1024x768 pt)", mm(768), mm(1024), QPrinter.Letter))

