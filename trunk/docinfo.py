# -*- coding: UTF-8 -*-

from xmlfactory import *

class DocInfo:
	def __init__(self, fn = None, owner = None, editor = None):
		self._fn = fn
		self._owner = owner
		self._editor = editor
		
	def staticTypeName(): return "DocInfo"
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return DocInfo()
	newInstance = staticmethod(newInstance)
	def typeName(self): return DocInfo.staticTypeName()
	
	def fn(self): return self._fn
	def owner(self): return self._owner
	def editor(self): return self._editor
	
	def setFn(self, fn): self._fn = fn
	def setOwner(self, owner): self._owner = owner
	def setEditor(self, editor): self._editor = editor

	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		sink.stepDown()
		sink.write("<fn>%s</fn>\n" % self.fn())
		sink.write("<owner>%s</owner>\n" % self.owner())
		sink.write("<editor>%s</editor>\n" % self.editor())
		sink.stepUp()
		sink.write("</%s>\n" % self.typeName())

	def readXml(self, source, path):
		path.append(self)
		source.get("<%s>" % self.typeName())
		source.get("<fn>")
		self._fn = source.get().value()
		source.get("</fn>")
		source.get("<owner>")
		self._owner = source.get().value()
		source.get("</owner>")
		source.get("<editor>")
		self._editor = source.get().value()
		source.get("</editor>")
		source.get("</%s>" % self.typeName())
		path.pop()

XmlFactory.instance(DocInfo).registerType(DocInfo)
