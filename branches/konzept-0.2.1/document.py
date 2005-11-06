# -*- coding: utf-8 -*-

from graph import *
from page import *
from grid import *
from xmlfactory import *
from indentsink import *
from memorysink import *

class Document:
	def __init__(self, graph = None, page = None, grid = None):
		self.setGraph(graph)
		self.setPage(page)
		self.setGrid(grid)
	
	def staticTypeName(): return "Document"
	staticTypeName = staticmethod(staticTypeName)
	
	def newInstance(): return Document()
	newInstance = staticmethod(newInstance)

	def typeName(self): return Document.staticTypeName()

	def setGraph(self, graph): self._graph = graph
	def graph(self): return self._graph
	
	def setPage(self, page): self._page = page
	def page(self): return self._page
	
	def setGrid(self, grid): self._grid = grid
	def grid(self): return self._grid
	
	def writeXml(self, sink):
		sink.write("<Document>\n")
		sink.stepDown()
		self.graph().writeXml(sink)
		self.page().writeXml(sink)
		if self.grid() != None:
			self.grid().writeXml(sink)
		sink.stepUp()
		sink.write("</Document>\n")

	def readXml(self, source, path = []):
		path.append(self)
		source.get("<Document>")
		self._graph = XmlFactory.instance(Graph).createFromXml(source, path).deepCopy()
		self._page = XmlFactory.instance(Page).createFromXml(source, path)
		if source.lookAhead() == tag("<Grid>"):
			self._grid = XmlFactory.instance(Grid).createFromXml(source, path)
		else:
			self._grid = None
		source.get("</Document>")
		path.pop()

	# == reading / writing message from XML string
	
	def toXml(self):
		mem = MemorySink()
		self.writeXml(IndentSink(mem))
		return mem.buf()
		
	def fromXml(self, s):
		self.readXml(XmlTokenSource(s), [])

	# == reading / writing message from XML string with leading length code
	
	def writeXmlFrame(self, sink):
		xml = self.toXml()
		lc = "%08X\n" % len(xml)
		sink.send(lc + xml)
		
	def readXmlFrame(self, source):
		lc = source.recv(8+len("\n"))
		lc = int(lc, 16)
		xml = source.recv(lc)
		self.fromXml(xml)

XmlFactory.instance(Document).registerType(Document)
