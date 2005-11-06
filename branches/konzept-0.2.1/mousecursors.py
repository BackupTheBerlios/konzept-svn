from qt import *

class MouseCursors:
	""" delivers global accessible mouse cursor objects """

	def __init__(self):
		self._pointingHandCursor = QCursor(Qt.PointingHandCursor)
		self._arrowCursor        = QCursor(Qt.ArrowCursor)
		self._sizeHorCursor      = QCursor(Qt.SizeHorCursor)
		self._sizeVerCursor      = QCursor(Qt.SizeVerCursor)
		self._sizeBDiagCursor    = QCursor(Qt.SizeBDiagCursor)
		self._sizeFDiagCursor    = QCursor(Qt.SizeFDiagCursor)
		self._sizeAllCursor      = QCursor(Qt.SizeAllCursor)
		self._crossCursor        = QCursor(Qt.CrossCursor)

	def pointingHandCursor(self): return self._pointingHandCursor
	def arrowCursor(self): return self._arrowCursor
	def sizeHorCursor(self): return self._sizeHorCursor
	def sizeVerCursor(self): return self._sizeVerCursor
	def sizeBDiagCursor(self): return self._sizeBDiagCursor
	def sizeFDiagCursor(self): return self._sizeFDiagCursor
	def sizeAllCursor(self): return self._sizeAllCursor
	def crossCursor(self): return self._crossCursor

mouseCursors = MouseCursors()

