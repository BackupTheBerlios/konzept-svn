# -*- coding: UTF-8 -*-

from graphedit import *
from qt import *

class GraphEditWindow(QWidget):
	nonameSerial = 0
	
	def __init__(self, mainWindow, filePath, parent, name, flags):
		QWidget.__init__(self, parent, name, flags)
		self._mainWindow = mainWindow
		gl = QGridLayout(self, 3, 3)
		self._graphEdit = GraphEdit(self)
		gl.addWidget(self._graphEdit, 1, 1)
		if filePath == None:
			filePath = ""
			while True:
				filePath = "noname_%d.kg" % GraphEditWindow.nonameSerial
				GraphEditWindow.nonameSerial = GraphEditWindow.nonameSerial + 1
				if not QFileInfo(filePath).exists(): break
		self.setFilePath(filePath)
		if str(QFileInfo(self._filePath).dirPath()) != "remote":
			self._mainWindow.documentOpened(self)

	def id(self): return object.__hash__(self)

	#def __del__(self):
	def closeEvent(self, e):
		if str(QFileInfo(self._filePath).dirPath()) != "remote":
			self._mainWindow.documentClosed(self)
		return QWidget.closeEvent(self, e)
	
	def graphEdit(self): return self._graphEdit
	
	def setFilePath(self, s):
		self._filePath = s
		caption = str(QFileInfo(s).fileName())
		if str(QFileInfo(self._filePath).dirPath()) == "remote":
			caption = caption + " (remote)"
		else:
			caption = caption + " (private)"
		self.setCaption(caption)
		self._mainWindow.documentRenamed(self)
		
	def filePath(self): return self._filePath
	
	def parent(self): return self._mainWindow