from qt import *
from uictextaligndlg import *

class TextAlignDlg(UicTextAlignDlg):

	def __init__(self, parent = None, name = None):
		UicTextAlignDlg.__init__(self, parent, name)
		
	def getAlign(self, align):
		if align & Qt.AlignTop != 0: 
			if align & Qt.AlignLeft != 0: self._r7.toggle()
			if align & Qt.AlignHCenter != 0: self._r8.toggle()
			if align & Qt.AlignRight != 0: self._r9.toggle()
		if align & Qt.AlignVCenter != 0:
			if align & Qt.AlignLeft != 0: self._r4.toggle()
			if align & Qt.AlignHCenter != 0: self._r5.toggle()
			if align & Qt.AlignRight != 0: self._r6.toggle()
		if align & Qt.AlignBottom != 0:
			if align & Qt.AlignLeft != 0: self._r1.toggle()
			if align & Qt.AlignHCenter != 0: self._r2.toggle()
			if align & Qt.AlignRight != 0: self._r3.toggle()
		ret = UicTextAlignDlg.exec_loop(self)
		if ret == QDialog.Rejected: return None
		align = 0
		if self._r7.isOn(): align = Qt.AlignTop | Qt.AlignLeft
		if self._r8.isOn(): align = Qt.AlignTop | Qt.AlignHCenter
		if self._r9.isOn(): align = Qt.AlignTop | Qt.AlignRight
		if self._r4.isOn(): align = Qt.AlignVCenter | Qt.AlignLeft
		if self._r5.isOn(): align = Qt.AlignVCenter | Qt.AlignHCenter
		if self._r6.isOn(): align = Qt.AlignVCenter | Qt.AlignRight
		if self._r1.isOn(): align = Qt.AlignBottom | Qt.AlignLeft
		if self._r2.isOn(): align = Qt.AlignBottom | Qt.AlignHCenter
		if self._r3.isOn(): align = Qt.AlignBottom | Qt.AlignRight
		return align
