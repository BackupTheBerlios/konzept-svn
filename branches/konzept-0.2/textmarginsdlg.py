# -*- coding: UTF-8 -*-

from uictextmarginsdlg import *

class TextMarginsDlg(UicTextMarginsDlg):
	def __init__(self, parent = None, name = None):
		UicTextMarginsDlg.__init__(self, parent, name)
		
	def getMargins(self, hm, vm):
		self.spinBox0.setValue(hm)
		self.spinBox1.setValue(vm)
		if self.exec_loop() == QDialog.Rejected: return None
		return (self.spinBox0.value(), self.spinBox1.value())

