# -*- coding: UTF-8 -*-

from sets import *

from qt import *
from mousecursors import *
from pageformatregistry import *

from transformframe import *
from nodeselectionshape import *
from connectorselectionshape import *

from node import *
from connector import *
from connectorset import *

from boxshape import *
from umlconnectorshape import *

from inlineeditor import *
from orderedset import *
 
from document import *
from graph import *
from page import *
from grid import *

from memorysink import *
from memorysource import *
from indentsink import *

from umlconnectorattributedlg import *
from textaligndlg import *
from textmarginsdlg import *

from sys import *

class GraphEdit(QScrollView):
	""" \brief Control and View according to the MVC model

		The GraphEdit is the central widgets which shows
		the graph visualization and allows interactive manipulation.
		The widget is state modelled. The initial state is listen mode,
		where the widget listens for user input. Input events that are
		recognised are assigned unique event numbers. A series of
		3 or less events make a up an input understood by this widget.
		Each reaction on such an event vector is defined in the eventListen() method.
		This method is also called the "event function" keeping the mathematical
		meaning in mind. It is defined like this: (event1, event2, event3) -> reaction.
		A reaction may be a state transition of the internal data structures
		representing the graph, but can also be a state transition of
		the GraphEdit's interaction state. The transitions of interaction state
		are performed by the begin*/end*/abort* methods.
	"""

	# interaction modes
	listenMode = 0             # misc mode
	transformMode = 1          # performing geometrical transformation on the selection
	connectorDragMode = 2      # dragging with middle mouse button pressed to connect two nodes
	selectionDragMode = 3      # creating a new selection by dragging with left mouse button hold
	inlineTextEditMode = 4     # editing text carried by some node or connector

	# event numbers
	leftMouseDown = 0
	leftMouseUp = 1
	noMouseMove = 2
	mouseMove = 3
	initialMouseMove = 4
	leftMouseDownShift = 5
	middleMouseDown = 6
	escKeyPress = 7
	delKeyPress = 8
	ctrlX = 9
	ctrlC = 10
	ctrlV = 11
	ctrlZ = 12
	ctrlY = 13
	leftMouseDoubleClick = 14

	def __init__(self, parent = None, name = None, flags = 0):
		QScrollView.__init__(self, parent, name, flags)

		self._graph = None
		
		self._interactionMode = GraphEdit.listenMode
		self._keepAspect = False # state variable for keep aspect mode

		self._events = [None, None, None]
		self._noMouseMove = True

		# current mouse cursor position
		self._cursorX = None
		self._cursorY = None
		self._cursorLabel = "select"
		
		# helper variable for connector drag and drop mode
		self._newConnector = None

		# memory variables for speeding up nodeBelowCursor()
		self._nodeBelowCursor_lastCursorX = None
		self._nodeBelowCursor_lastCursorY = None
		self._nodeBelowCursor = None

		# memory variables for speeding up connectorBelowCursor()
		self._connectorBelowCursor_lastCursorX = None
		self._connectorBelowCursor_lastCursorY = None
		self._connectorBelowCursor = None
		self._connectorSetBelowCursor = None
		self._connectorSignBelowCursor = None

		# Qt widget setup
		self.viewport().setBackgroundMode(Qt.PaletteDark)
		self._desktopColor = self.viewport().paletteBackgroundColor()
		self.viewport().setBackgroundMode(Qt.NoBackground)
		self.viewport().setMouseTracking(True)                         # to receive mouse move events
		self.setFocusPolicy(QWidget.StrongFocus)
		
		# hack needed to center contents if viewport is larger than contents
		# (sorry for that, the whole shit code needs rewrite!;)
		self._contentsDisplacementX = 0
		self._contentsDisplacementY = 0
		
		self._selectionDragBox = BoundingBox(0,0,1,1)
		self._selectionDragFrame = TransformFrame(self._selectionDragBox)
		
		self._inlineEditor = InlineEditor(self)

	def setPage(self, pg):
		self._page = pg
		self.resizeContents(pg.width(), pg.height())
		self.viewportResizeEvent(QResizeEvent(self.viewport().size(), self.viewport().size()))
	
	def page(self): return self._page

	def setGraph(self, graph):
		if self._graph != None:
			self.graph().nodes().unlinkTriggers()
			self.graph().connectorSets().unlinkTriggers()
		self._graph = graph
		self._nodeSelectionShape = NodeSelectionShape(self.graph().nodeSelection())
		self._connectorSelectionShape = ConnectorSelectionShape(self.graph().connectorSelection())
	
	def graph(self): return self._graph
	
	def setGrid(self, grid): self._grid = grid
	def grid(self): return self._grid 
	
	def setDocument(self, d):
		self.setGraph(d.graph())
		self.setPage(d.page())
		self.setGrid(d.grid())
	
	def document(self): return Document(self.graph(), self.page(), self.grid())
	
	def interactionMode(self): return self._interactionMode

	
	# ===== misc. methods

	def cursorX(self): return self._cursorX
	def cursorY(self): return self._cursorY
	
	def pageX0(self):
		x0 = self.contentsX()
		if self._contentsDisplacementX != 0: x0 = self._contentsDisplacementX
		return x0
		
	def pageY0(self):
		y0 = self.contentsY()
		if self._contentsDisplacementY != 0: y0 = self._contentsDisplacementY
		return y0
	
	def drawTo(self, p):
		""" draw the contents of this GraphEdit to a certain QPainter
		"""
		
		# p.scale(1.5,1.5)
		pen = QPen()
		pen.setColor(Qt.black)
		pen.setWidth(1)
		p.setPen(pen)
		
		font = QFont("Sans")
		font.setPixelSize(10)
		p.setFont(font)
		# print "p.font().pixelSize() =", p.font().pixelSize()
		
		for node in self.graph().nodes():
			node.shape().drawTo(p)
		for cs in self.graph().connectorSets():
			cs.drawTo(p)
		self._nodeSelectionShape.drawTo(p)
		self._connectorSelectionShape.drawTo(p)
		if self.interactionMode() == GraphEdit.connectorDragMode:
			self._newConnector.shape().drawTo(p)
		elif self.interactionMode() == GraphEdit.selectionDragMode:
			self._selectionDragFrame.drawTo(p)

	def drawPageTo(self, p):
		p.fillRect(self.viewport().rect(), QBrush(self._desktopColor))
		p.translate(-self.pageX0(), -self.pageY0())
		p.setBrush(Qt.white)
		p.drawRect(0, 0, self.contentsWidth(), self.contentsHeight())
	
	def nodeBelowCursor(self):
		hasMoved = self._nodeBelowCursor_lastCursorX != self._cursorX or \
		           self._nodeBelowCursor_lastCursorY != self._cursorY

		if hasMoved:
			self._nodeBelowCursor_lastCursorX = self._cursorX
			self._nodeBelowCursor_lastCursorY = self._cursorY

			for node in self.graph().nodes():
				if node.shape().containsPoint(self._cursorX, self._cursorY):
					self._nodeBelowCursor = node
					break
			else:
				self._nodeBelowCursor = None

		return self._nodeBelowCursor

	def invalidateNodeBelowCursor(self):
		self._nodeBelowCursor_lastCursorX = None 
		self._nodeBelowCursor_lastCursorY = None
	
	def connectorBelowCursor(self):
		hasMoved = self._connectorBelowCursor_lastCursorX != self._cursorX or \
		           self._connectorBelowCursor_lastCursorY != self._cursorY

		if hasMoved:
			self._connectorBelowCursor_lastCursorX = self._cursorX
			self._connectorBelowCursor_lastCursorY = self._cursorY

			for cs in self.graph().connectorSets():
				c2 = None
				sign = None
				for c in cs.positiveConnectors():
					if c.shape().containsPoint(self._cursorX, self._cursorY):
						c2 = c
						sign = "+"
						break
				if c2 == None:
					for c in cs.negativeConnectors():
						if c.shape().containsPoint(self._cursorX, self._cursorY):
							c2 = c
							sign = "-"
							break
				if c2 != None:
					self._connectorBelowCursor = c2
					self._connectorSetBelowCursor = cs
					self._connectorSignBelowCursor = sign
					break
			else:
				self._connectorBelowCursor = None
				self._connectorSetBelowCursor = None

		return self._connectorBelowCursor
		
	def connectorBelowCursorEx(self):
		self.connectorBelowCursor()
		return (self._connectorBelowCursor, self._connectorSetBelowCursor, self._connectorSignBelowCursor)

	def updateMouseCursor(self):
		(x, y) = (self._cursorX, self._cursorY)
		if self._nodeSelectionShape.containsPoint(x, y):
			self.setCursor(self._nodeSelectionShape.getCursor(x, y))
			self._cursorLabel = "transform"
		elif self.nodeBelowCursor() != None \
		or self.connectorBelowCursor() != None:
			self.setCursor(mouseCursors.pointingHandCursor())
			self._cursorLabel = "select"
		else:
			self.setCursor(mouseCursors.arrowCursor())
			if self.graph().nodeShapePrototype() != None:
				self._cursorLabel = "create"
			else:
				self._cursorLabel = "select"
		self.parent().parent().statusBar().message(self._cursorLabel)

	def snapNodeSelectionToGrid(self):
		""" align node centers to grid lines """
		if self.grid() != None:
			for node in self.graph().nodeSelection():
				s = node.shape()
				(cx, cy) = self.grid().nearest(s.cx(), s.cy())
				s.moveCenter(cx, cy)
			self._nodeSelectionShape.updateSize()
			self.updateContents()
	
	# ===== interaction mode transitions

	def beginTransform(self, forRectangle):
		self._keepAspect = False    # hack to prevent aspect scaling problems
		cursor = self._nodeSelectionShape.transformFrame().beginTransform(self._cursorX, self._cursorY)
		if (self._keepAspect):
			cursor = mouseCursors.crossCursor()
		if cursor != None:
			self.setCursor(cursor)
		self._nodeSelectionShape.transformFrame().setKeepAspect(self._keepAspect)
		self._interactionMode = GraphEdit.transformMode
		self.graph().beforeModified()
		
	def endTransform(self):
		self._nodeSelectionShape.transformFrame().endTransform()
		self.snapNodeSelectionToGrid()
		self.updateMouseCursor()
		self._interactionMode = GraphEdit.listenMode
		self.graph().modified()

	def abortTransform(self):
		self._nodeSelectionShape.transformFrame().abortTransform()
		self.updateContents()
		self.updateMouseCursor()
		self._interactionMode = GraphEdit.listenMode

	def beginConnectorDrag(self):
		if self.graph().somethingSelected():
			self.graph().unselectAll()
			self.updateContents()
		self._interactionMode = GraphEdit.connectorDragMode
		self._newConnector = Connector(self.graph().connectorShapePrototype().copy())
		self._newConnector.setNode0(self.nodeBelowCursor())

	def endConnectorDrag(self):
		if self.nodeBelowCursor() != None \
		and self.nodeBelowCursor() != self._newConnector.node0():
			self._newConnector.setNode1(self.nodeBelowCursor())
			self._newConnector.calcP0P1()
			self.graph().addConnector(self._newConnector)
		self._newConnector = None
		self._interactionMode = GraphEdit.listenMode
		self.updateContents()

	def beginSelectionDrag(self):
		if self.graph().somethingSelected(): self.graph().unselectAll()
		self._selectionDragBox.setCoords(self._cursorX, self._cursorY, self._cursorX + 1, self._cursorY + 1)
		self._selectionDragFrame.beginTransform(self._cursorX, self._cursorY, TransformFrame.moveX1Y1)
		self._interactionMode = GraphEdit.selectionDragMode
	
	def endSelectionDrag(self):
		self._selectionDragFrame.endTransform()
		self._interactionMode = GraphEdit.listenMode
		for node in self.graph().nodes():
			s = node.shape()
			if self._selectionDragBox.containsPoint(s.x0(), s.y0()) \
			and self._selectionDragBox.containsPoint(s.x1(), s.y1()):
				self.graph().addToNodeSelection(node)
		self.graph().stateChanged()
		self.updateContents()
	
	def beginInlineTextEdit(self):
		if self.interactionMode() == GraphEdit.inlineTextEditMode:
			self.endInlineTextEdit()
		if self.graph().somethingSelected(): self.graph().unselectAll()
		self._interactionMode = GraphEdit.inlineTextEditMode
		self._inlineEditor.beginEditing(self.nodeBelowCursor().shape())
		self.setCursor(mouseCursors.arrowCursor())
		self.graph().beforeModified()

	def endInlineTextEdit(self):
		self._inlineEditor.endEditing()
		self._interactionMode = GraphEdit.listenMode
		self.updateMouseCursor()
		self.setFocus()
		self.graph().modified()

	# ===== Qt event handler

	def viewportResizeEvent(self, event):
		bg = QPixmap(event.size().width(), event.size().height())
		self._backBuffer = bg
		if (bg.width() > self.contentsWidth()):
			self._contentsDisplacementX = (self.contentsWidth() - bg.width()) / 2
		else:
			self._contentsDisplacementX = 0
		if (bg.height() > self.contentsHeight()):
			self._contentsDisplacementY = (self.contentsHeight() - bg.height()) / 2
		else:
			self._contentsDisplacementY = 0
			
	def viewportPaintEvent(self, event):
		bg = self._backBuffer
		p = QPainter()
		p.begin(bg)
		self.drawPageTo(p)
		if self.grid() != None:
			self.grid().drawTo(p, self.contentsWidth(), self.contentsHeight())
		self.drawTo(p)
		# cursor label feature
		"""if self._cursorX != None and self._cursorY != None:
			p.pen().setColor(Qt.gray)
			p.drawText(self._cursorX+14, self._cursorY+6, self._cursorLabel)"""
		p.end()
		bitBlt(self.viewport(), 0, 0, bg, 0, 0, bg.width(), bg.height(), Qt.CopyROP, True)
	
	def contentsMousePressEvent(self, event):
		self._cursorX = event.x() + self._contentsDisplacementX
		self._cursorY = event.y() + self._contentsDisplacementY
		
		if self.interactionMode() == GraphEdit.transformMode:
			if event.button() == Qt.RightButton:
				self.abortTransform()

		elif self.interactionMode() == GraphEdit.listenMode:
			self._noMouseMove = True
			if event.button() == Qt.LeftButton and event.state() == 0:
				self._events.append(GraphEdit.leftMouseDown)
				self.eventListen()
			elif event.button() == Qt.LeftButton and event.state() == Qt.ShiftButton:
				self._events.append(GraphEdit.leftMouseDownShift)
				self.eventListen()
			elif (event.button() == Qt.MidButton and event.state() == 0) \
			or (event.button() == Qt.LeftButton and event.state() == Qt.ControlButton):
				self._events.append(GraphEdit.middleMouseDown)
				self.eventListen()

		elif self.interactionMode() == GraphEdit.inlineTextEditMode:
			if not self._inlineEditor.shape().containsPoint(self._cursorX, self._cursorY):
				self.endInlineTextEdit()
				if self.nodeBelowCursor() != None: self.mousePressEvent(event)

	def contentsMouseDoubleClickEvent(self, event):
		if event.button() == Qt.LeftButton and event.state() == 0:
			self._events.append(GraphEdit.leftMouseDoubleClick)
			self.eventListen()

	def contentsMouseReleaseEvent(self, event):
		if self.interactionMode() == GraphEdit.transformMode:
			if event.button() == Qt.LeftButton:
				self.endTransform()

		elif self.interactionMode() == GraphEdit.selectionDragMode:
			if event.button() == Qt.LeftButton:
				self.endSelectionDrag()
		
		elif self.interactionMode() == GraphEdit.connectorDragMode:
			if event.button() == Qt.MidButton or event.button() == Qt.LeftButton:
				self.endConnectorDrag()

		elif self.interactionMode() == GraphEdit.listenMode:
			if self._noMouseMove == True:
				self._events.append(GraphEdit.noMouseMove)
				self.eventListen()
			if event.button() == Qt.LeftButton:
				self._events.append(GraphEdit.leftMouseUp)
				self.eventListen()

	def contentsMouseMoveEvent(self, event):
		self._cursorX = event.x() + self._contentsDisplacementX
		self._cursorY = event.y() + self._contentsDisplacementY
		
		if self.interactionMode() == GraphEdit.transformMode:
			"""gp = self.mapFromGlobal(QCursor.pos())
			if gp.x() < 0 or gp.x() >= self.width() or \
			   gp.y() < 0 or gp.y() >= self.height():
				print "Out of range!
			# if QCursor.pos().x <"""
			self._nodeSelectionShape.transformFrame().mouseMoveEvent(self._cursorX, self._cursorY)
			self.repaintContents()

		elif self.interactionMode() == GraphEdit.selectionDragMode:
			self._selectionDragFrame.mouseMoveEvent(self._cursorX, self._cursorY)
			self.repaintContents()
		
		elif self.interactionMode() == GraphEdit.connectorDragMode:
			self._newConnector.dragP1(array([self._cursorX, self._cursorY]))
			self.repaintContents()

		elif self.interactionMode() == GraphEdit.listenMode:
			if self._events[-1] != GraphEdit.mouseMove:
				self._events.append(GraphEdit.mouseMove)
			self._noMouseMove = False
			self.updateMouseCursor()
			self.eventListen()
			# self.repaintContents()                      # cursor label feature
	
	def leaveEvent(self, event):
		self._cursorX = None
		self._cursorY = None
		self.repaintContents()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Shift:
			if not self._keepAspect:
				self._keepAspect = True
				if self.interactionMode() == GraphEdit.transformMode:
					self._nodeSelectionShape.transformFrame().setKeepAspect(self._keepAspect)
					self.setCursor(mouseCursors.crossCursor())
		elif event.key() == Qt.Key_Escape:
			if self.interactionMode() == GraphEdit.transformMode:
				self.abortTransform()
			elif self.interactionMode() == GraphEdit.listenMode:
				self._events.append(GraphEdit.escKeyPress)
				self.eventListen()
		elif event.key() == Qt.Key_Delete \
		or event.key() == Qt.Key_D and event.state() == Qt.ControlButton:
			if self.interactionMode() == GraphEdit.listenMode:
				self._events.append(GraphEdit.delKeyPress)
				self.eventListen()
		elif event.key() == Qt.Key_X \
		and event.state() == Qt.ControlButton:
			self._events.append(GraphEdit.ctrlX)
			self.eventListen()
		elif event.key() == Qt.Key_C \
		and event.state() == Qt.ControlButton:
			self._events.append(GraphEdit.ctrlC)
			self.eventListen()
		elif event.key() == Qt.Key_V \
		and event.state() == Qt.ControlButton:
			self._events.append(GraphEdit.ctrlV)
			self.eventListen()

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Shift:
			if self._keepAspect:
				self._keepAspect = False
				if self.interactionMode() == GraphEdit.transformMode:
					self._nodeSelectionShape.transformFrame().setKeepAspect(self._keepAspect)
					self.setCursor(self._nodeSelectionShape.transformFrame().getCursorShapeByMode())

	"""def focusOutEvent(self, event):
		self._graph.unselectAll()
		self.updateContents()"""
	
	def contextMenuEvent(self, event):
		c = self.connectorBelowCursor()
		k = self.nodeBelowCursor()
		a = self._nodeSelectionShape.containsPoint(self._cursorX, self._cursorY)
		b = self._connectorSelectionShape.connectorBelowCursor(self._cursorX, self._cursorY) != None
		nn = self.graph().nodeSelection().count()
		nc = self.graph().connectorSelection().count()
		
		sc = ((a and b) and (nn + nc > 1)) # selection context
		mnc = a and (nn > 1) # multiple node context
		mcc = b and (nc > 1) # multiple connector context
		
		if sc or mnc:
			"""if sc: print "selection context"
			if mnc: print "multiple node context"
			"""
			pm = QPopupMenu(self)
			id0 = pm.insertItem("Text Alignment")
			id1 = pm.insertItem("Fill Color")
			id2 = pm.insertItem("Margins")
			pm.insertSeparator()
			id3 = pm.insertItem("Optimal Size")
			id4 = pm.insertItem("Same Width")
			id5 = pm.insertItem("Same Height")
			id6 = pm.insertItem("Same Size")
			pm.insertSeparator()
			id7 = pm.insertItem("Line up Horizontal")
			id8 = pm.insertItem("Line up Vertical")
			pm.insertSeparator()
			id9 = pm.insertItem("Cut")
			id10 = pm.insertItem("Copy")
			id11 = pm.insertItem("Paste")
			pm.setAccel(QKeySequence("CTRL+X"), id9)
			pm.setAccel(QKeySequence("CTRL+C"), id10)
			pm.setAccel(QKeySequence("CTRL+V"), id11)
			ret = pm.exec_loop(self.mapToGlobal(QPoint(self._cursorX - self._contentsDisplacementX + 1, self._cursorY - self._contentsDisplacementY + 1)))
			if k == None: k = self.graph().nodeSelection().top()
			if ret == id0:
				align = TextAlignDlg(self).getAlign(k.shape().textAlign())
				if align != None:
					for node in self.graph().nodeSelection():
						node.shape().selectActive()
						node.shape().setTextAlign(align)
					self.updateContents()
			elif ret == id1:
				color = QColorDialog.getColor(k.shape().bgColor())
				if color.isValid():
					for node in self.graph().nodeSelection():
						node.shape().selectActive()
						node.shape().setBgColor(color)
					self.updateContents()
			elif ret == id2:
				margins = TextMarginsDlg(self).getMargins(k.shape().hMargin(), k.shape().vMargin())
				if margins != None:
					for node in self.graph().nodeSelection():
						node.shape().selectActive()
						node.shape().setHMargin(margins[0])
						node.shape().setVMargin(margins[1])
						node.shape().optimizeSize()
					self._nodeSelectionShape.updateSize()
					self.updateContents()
			elif ret == id3:
				for node in self.graph().nodeSelection():
					node.shape().optimizeSize()
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id4:
				mw = 1
				for node in self.graph().nodeSelection():
					s = node.shape()
					if s.width() > mw: mw = s.width()
				for node in self.graph().nodeSelection():
					node.shape().resize(mw, node.shape().height())
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id5:
				mh = 1
				for node in self.graph().nodeSelection():
					s = node.shape()
					if s.height() > mh: mh = s.height()
				for node in self.graph().nodeSelection():
					node.shape().resize(node.shape().width(), mh)
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id6:
				(mw, mh) = (1, 1)
				for node in self.graph().nodeSelection():
					s = node.shape()
					if s.width() > mw: mw = s.width()
					if s.height() > mh: mh = s.height()
				for node in self.graph().nodeSelection():
					node.shape().resize(mw,mh)
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id7:
				(cx, cy) = (k.shape().cx(), k.shape().cy())
				for node in self.graph().nodeSelection():
					node.shape().moveCenter(node.shape().cx(), cy)
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id8:
				(cx, cy) = (k.shape().cx(), k.shape().cy())
				for node in self.graph().nodeSelection():
					node.shape().moveCenter(cx, node.shape().cy())
				self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id9:
				self.ctrlX()
			elif ret == id10:
				self.ctrlC()
			elif ret == id11:
				self.ctrlV()
		elif mcc:
			# print "multiple connector context"
			None
			
		elif k != None:
			# print "single node context"
			pm = QPopupMenu(self)
			id0 = pm.insertItem("Text Alignment")
			id1 = pm.insertItem("Fill Color")
			id2 = pm.insertItem("Margins")
			pm.insertSeparator()
			id3 = pm.insertItem("Optimal Size")
			pm.insertSeparator()
			id4 = pm.insertItem("Edit Text")
			pm.insertSeparator()
			id5 = pm.insertItem("Cut")
			id6 = pm.insertItem("Copy")
			id7 = pm.insertItem("Paste")
			pm.setAccel(QKeySequence("CTRL+X"), id5)
			pm.setAccel(QKeySequence("CTRL+C"), id6)
			pm.setAccel(QKeySequence("CTRL+V"), id7)
			ret = pm.exec_loop(self.mapToGlobal(QPoint(self._cursorX - self._contentsDisplacementX + 1, self._cursorY - self._contentsDisplacementY + 1)))
			k.shape().selectActive(self._cursorX, self._cursorY)
			if ret == id0: 
				align = TextAlignDlg(self).getAlign(k.shape().textAlign())
				if align != None:
					k.shape().setTextAlign(align)
					self.updateContents()
			elif ret == id1:
				color = QColorDialog.getColor(k.shape().bgColor())
				if color.isValid(): k.shape().setBgColor(color)
			elif ret == id2:
				margins = TextMarginsDlg(self).getMargins(k.shape().hMargin(), k.shape().vMargin())
				if margins != None:
					k.shape().setHMargin(margins[0])
					k.shape().setVMargin(margins[1])
					k.shape().optimizeSize()
					if self.graph().nodeSelection().count() > 0: 
						self._nodeSelectionShape.updateSize()
					self.updateContents()
			elif ret == id3:
				k.shape().optimizeSize()
				if self.graph().nodeSelection().count() > 0: 
					self._nodeSelectionShape.updateSize()
				self.updateContents()
			elif ret == id4:
				self.beginInlineTextEdit()
			elif ret == id5:
				self.ctrlX()
			elif ret == id6:
				self.ctrlC()
			elif ret == id7:
				self.ctrlV()
		else:
			pm = QPopupMenu(self)
			id0 = pm.insertItem("Cut")
			id1 = pm.insertItem("Copy")
			id2 = pm.insertItem("Paste")
			pm.setAccel(QKeySequence("CTRL+X"), id0)
			pm.setAccel(QKeySequence("CTRL+C"), id1)
			pm.setAccel(QKeySequence("CTRL+V"), id2)
			ret = pm.exec_loop(self.mapToGlobal(QPoint(self._cursorX - self._contentsDisplacementX + 1, self._cursorY - self._contentsDisplacementY + 1)))
			if ret == id0:
				self.ctrlX()
			elif ret == id1:
				self.ctrlC()
			elif ret == id2:
				self.ctrlV()
	
	# ===== mouse click to keyboard press translations
	
	def ctrlX(self):
		self._events.append(GraphEdit.ctrlX)
		self.eventListen()
		
	def ctrlC(self):
		self._events.append(GraphEdit.ctrlC)
		self.eventListen()
	
	def ctrlV(self):
		self._events.append(GraphEdit.ctrlV)
		self.eventListen()
		
	def ctrlZ(self):
		self._events.append(GraphEdit.ctrlZ)
		self.eventListen()
		
	def ctrlY(self):
		self._events.append(GraphEdit.ctrlY)
		self.eventListen()
	
	# ===== definition of the interaction function

	def eventListen(self):
		""" Listens on the user's input commands and
		    tries to makes sense out of it. Each input command is defined
		    by a combination of at max 3 events from the input devices
		    and the cursor placement.
		"""
		
		# create node
		if self._events[-1] == GraphEdit.leftMouseDown \
		and self.nodeBelowCursor() == None \
		and not self._nodeSelectionShape.containsPoint(self._cursorX, self._cursorY) \
		and not self.connectorBelowCursor() != None \
		and self.graph().nodeShapePrototype() != None:
			self.graph().createNode(self._cursorX, self._cursorY)
			self.snapNodeSelectionToGrid()
			self.invalidateNodeBelowCursor()
			self.updateMouseCursor()
			self.updateContents()
			self._events = [None, None, None]

		# select single node
		elif self._events[-3] == GraphEdit.leftMouseDown \
		and self._events[-2] == GraphEdit.noMouseMove \
		and self._events[-1] == GraphEdit.leftMouseUp \
		and self.nodeBelowCursor() != None \
		and self.nodeBelowCursor() not in self.graph().nodeSelection():
			self.graph().selectSingleNode(self.nodeBelowCursor())
			self.updateContents()
			self._events = [None, None, None]
			
		# select single connector
		elif self._events[-3] == GraphEdit.leftMouseDown \
		and self._events[-2] == GraphEdit.noMouseMove \
		and self._events[-1] == GraphEdit.leftMouseUp \
		and self.connectorBelowCursor() != None \
		and self.connectorBelowCursor() not in self.graph().connectorSelection():
			self.graph().selectSingleConnector(self.connectorBelowCursor())
			self.updateContents()
			self._events = [None, None, None]

		# destroy selection
		elif ((self._events[-3] == GraphEdit.leftMouseDown \
		and self._events[-2] == GraphEdit.noMouseMove \
		and self._events[-1] == GraphEdit.leftMouseUp) \
		or self._events[-1] == GraphEdit.escKeyPress) \
		and self.graph().nodeSelection().count() + self.graph().connectorSelection().count() > 0:
			self.graph().unselectAll()
			self.updateContents()
			self.updateMouseCursor()
			self._events = [None, None, None]
		
		# start transforming node selection
		elif (self._events[-2] == GraphEdit.leftMouseDown \
		or self._events[-2] == GraphEdit.leftMouseDownShift) \
		and self._events[-1] == GraphEdit.mouseMove \
		and self._nodeSelectionShape.containsPoint(self._cursorX, self._cursorY):
			self._events = [None, None, None]
			self.beginTransform(self.nodeBelowCursor())

		# select single node and start move transform
		elif self._events[-2] == GraphEdit.leftMouseDown \
		and self._events[-1] == GraphEdit.mouseMove \
		and self.nodeBelowCursor() != None \
		and self.nodeBelowCursor() not in self.graph().nodeSelection():
			self.graph().selectSingleNode(self.nodeBelowCursor())
			self.updateContents()
			self._events = [None, None, None]
			self.beginTransform(self.nodeBelowCursor())

		# add node to node selection
		elif self._events[-1] == GraphEdit.leftMouseDownShift \
		and self.nodeBelowCursor() != None \
		and self.nodeBelowCursor() not in self.graph().nodeSelection():
			self.graph().addToNodeSelection(self.nodeBelowCursor())
			self.updateContents()
			self._events = [None, None, None]

		# add connector to connector selection
		elif self._events[-1] == GraphEdit.leftMouseDownShift \
		and self.connectorBelowCursor() != None \
		and self.connectorBelowCursor() not in self.graph().connectorSelection():
			self.graph().addToConnectorSelection(self.connectorBelowCursor())
			self.updateContents()
			self._events = [None, None, None]

		# remove single node from node selection
		elif self._events[-1] == GraphEdit.leftMouseDownShift \
		and self.nodeBelowCursor() != None \
		and self.nodeBelowCursor() in self.graph().nodeSelection():
			self.graph().removeFromNodeSelection(self.nodeBelowCursor())
			self.updateContents()
			self._events = [None, None, None]

		# remove single connector from connector selection
		elif self._events[-1] == GraphEdit.leftMouseDownShift \
		and self.connectorBelowCursor() != None \
		and self.connectorBelowCursor() in self.graph().connectorSelection():
			self.graph().removeFromConnectorSelection(self.connectorBelowCursor())
			self.updateContents()
			self._events = [None, None, None]

		# deleting all selected nodes and all selected connectors
		elif self._events[-1] == GraphEdit.delKeyPress \
		and ( self.graph().nodeSelection().count() != 0 or \
		      self.graph().connectorSelection().count() != 0 ):
			self.graph().deleteSelection()
			self.updateContents()
			self._events = [None, None, None]
			self.updateMouseCursor()

		# enter connector drag mode
		elif self._events[-1] == GraphEdit.middleMouseDown \
		and self.nodeBelowCursor() != None \
		and self.graph().connectorShapePrototype() != None:
			self.beginConnectorDrag()
			self._events = [None, None, None]
		
		# enter selection drag mode
		elif (self._events[-2] == GraphEdit.leftMouseDownShift \
		or self._events[-2] == GraphEdit.leftMouseDown) \
		and self._events[-1] == GraphEdit.mouseMove \
		and not self._nodeSelectionShape.containsPoint(self._cursorX, self._cursorY):
			self.beginSelectionDrag()
			self.updateContents()
			self._events = [None, None, None]
		
		# start inline text edit mode for a single node
		elif self._events[-1] == GraphEdit.leftMouseDoubleClick \
		and self.nodeBelowCursor() != None:
			self.beginInlineTextEdit()
			self._events = [None, None, None]
		
		# open connector attributes dialog
		elif self._events[-1] == GraphEdit.leftMouseDoubleClick \
		and self.connectorBelowCursor() != None:
			dlg = UmlConnectorAttributeDlg(self)
			dlg.setConnector(self.connectorBelowCursor())
			dlg.exec_loop()
			self.updateContents()
			self._events = [None, None, None]
		
		# cut
		elif self._events[-1] == GraphEdit.ctrlX \
		and self.graph().nodeSelection().count() > 0:
			g2 = self.graph().copySelection()
			self.graph().deleteSelection()
			m = MemorySink()
			sink = IndentSink(m)
			sink.write('<?xml version="1.0" standalone="yes"?>\n')
			g2.writeXml(sink)
			cb = QApplication.clipboard()
			cb.setText(m.buf(), QClipboard.Clipboard)
			self.updateContents()
			self._events = [None, None, None]
		
		# copy
		elif self._events[-1] == GraphEdit.ctrlC \
		and self.graph().nodeSelection().count() > 0:
			g2 = self.graph().copySelection()
			m = MemorySink()
			sink = IndentSink(m)
			sink.write('<?xml version="1.0" standalone="yes"?>\n')
			g2.writeXml(sink)
			cb = QApplication.clipboard()
			cb.setText(m.buf(), QClipboard.Clipboard)
			self._events = [None, None, None]
		
		# paste
		elif self._events[-1] == GraphEdit.ctrlV:
			if self.graph().somethingSelected(): self.graph().unselectAll()
			cb = QApplication.clipboard()
			g2 = Graph()
			source = XmlTokenSource(str(cb.text()))
			g2.readXml(source)
			self.graph().insertGraph(g2)
			self.updateContents()
			self._events = [None, None, None]

		# undo
		elif self._events[-1] == GraphEdit.ctrlZ:
			if self.graph().history().canUndo():
				print "undo"
				self.graph().unselectAll()
				self.setGraph(self.graph().history().undo(self.graph()))
				self.updateContents()
			else:
				print "can't undo"

		# redo
		elif self._events[-1] == GraphEdit.ctrlY:
			if self.graph().history().canRedo():
				print "redo"
				self.graph().unselectAll()
				self.setGraph(self.graph().history().redo(self.graph()))
				self.updateContents()
			else:
				print "can't redo"
