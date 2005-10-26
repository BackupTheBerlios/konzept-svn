# -*- coding: UTF-8 -*-

from uicumlconnectorattributedlg import *

class UmlConnectorAttributeDlg(UicUmlConnectorAttributeDlg):
	def __init__(self, parent = None, name = None):
		UicUmlConnectorAttributeDlg.__init__(self, parent, name)
		self._c = None
		
	def setConnector(self, c):
		self._c = c
		s = c.shape()
		if s.label0() == None:
			self.lineEdit0.setReadOnly(True)
			self.lineEdit0.setBackgroundMode(Qt.PaletteBackground)
		if s.label1() == None:
			self.lineEdit1.setReadOnly(True)
			self.lineEdit1.setBackgroundMode(Qt.PaletteBackground)
		if s.label0() != None: self.lineEdit0.setFocus()
		else: self.lineEdit1.setFocus()
	
	def exec_loop(self):
		self.lineEdit0.setText(self._c.shape().label0())
		self.lineEdit1.setText(self._c.shape().label1())
		ret = UicUmlConnectorAttributeDlg.exec_loop(self)
		if ret == QDialog.Accepted:
			s = self._c.shape()
			s.setLabel0(str(self.lineEdit0.text().ascii()))
			s.setLabel1(str(self.lineEdit1.text().ascii()))
