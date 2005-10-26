# -*- coding: utf-8 -*-

from qt import *
from pageformatregistry import *
from xmlfactory import *

def pt(mm): return int(mm*72.27/25.4)

class Page:
	def __init__(self, format = None, orientation = None):
		self._format = format
		self._orientation = orientation
		
	def staticTypeName(): return "Page"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return Page()
	newInstance = staticmethod(newInstance)

	def typeName(self): return Page.staticTypeName()

	def format(self): return self._format
	def setFormat(self, pageFormat): self._pageFormat = pageFormat
	
	def width(self):
		if self._orientation == QPrinter.Portrait: return pt(self._format.width())
		else: return pt(self._format.height())

	def height(self):
		if self._orientation == QPrinter.Portrait: return pt(self._format.height())
		else: return pt(self._format.width())
		
	def orientation(self): return self._orientation

	def writeXml(self, sink):
		sink.write("<Page>\n")
		sink.stepDown()
		sink.write("<format>%s</format>\n" % self.format().name())
		sink.write("<orientation>%d</orientation>\n" % self.orientation())
		sink.stepUp()
		sink.write("</Page>\n")

	def readXml(self, source, path = []):
		path.append(self)
		source.get("<Page>")
		source.get("<format>")
		i = pageFormatRegistry.getIndex(PageFormat(source.get().value()))
		self._format = pageFormatRegistry[i]
		source.get("</format>")
		source.get("<orientation>")
		self._orientation = int(source.get().value())
		source.get("</orientation>")
		source.get("</Page>")
		path.pop()

XmlFactory.instance(Page).registerType(Page)