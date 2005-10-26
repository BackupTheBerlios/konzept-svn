# -*- coding: utf-8 -*-

from qt import *

class ToolDockWindow(QDockWindow):
	""" A tool box in a dock window as used in the Qt designer.
	    Allows so select different tools from different tool groups.
	    By default nothing is selected. From a single group exactly one
	    tool can be selected at the same time. More than one tools
	    can be selected from different groups. """
	
	def __init__(self, parent = None, name = None):
		QDockWindow.__init__(self, parent, name)
		
		self.setResizeEnabled(True)
		self.setCloseMode(QDockWindow.Always)
		self.setFixedExtentWidth(160)
		self.setCaption("Graph Elements")
		self.setWidget(QToolBox(self))
		
		self._btnStyle = QStyleFactory.create("windows")
		
		# maps a toolbar name to a button group
		self._buttonGroups = {}
		
		# maps a tool name to a tool description vector
		self._tools = {}
		
	def addGroup(self, name, toolList):
		self.createToolBar(self.parent(), self.widget(), name, toolList)
	
	def selected(self, tbarName):
		bg = self._buttonGroups[tbarName]
		btn = bg.selected()
		if btn == None: return None
		return self._tools[tbarName + btn.name()]
	
	def unselect(self):
		for name in self._buttonGroups:
			btn = self._buttonGroups[name].selected()
			if btn != None: btn.setOn(False)
	
	def nodeType(self): return self._buttonGroups[0].selectedId()
	def connectorType(self): return self._buttonGroups[1].selectedId()
	
	def clicked(self, id):
		self.emit(PYSIGNAL("selectionChanged"), ())

	def createToolBar(self, parent, tbox, name, actions):
		tbar = QToolBar(None, None, tbox, False, name)
		tbar.setFrameStyle(QFrame.NoFrame)
		tbar.setOrientation(Qt.Vertical)
		tbar.setBackgroundMode(Qt.PaletteBase)
		
		for a in actions:
			qa = QAction(QIconSet(QPixmap(str(qApp.applicationDirPath())+"/images/"+a[1])), a[0], a[3], parent, a[2])
			qa.setToggleAction(True)
			qa.addTo(tbar)
		
		# tbar.children()[-len(actions)].toggle()
		
		bg = QButtonGroup()
		self._buttonGroups[name] = bg
		bg.setExclusive(True)
		self.connect(bg, SIGNAL("clicked(int)"), self.clicked)
		for i in range(len(actions)):
			btn = tbar.children()[-(i+1)]
			btn.setStyle(self._btnStyle)
			btn.setBackgroundMode(tbar.backgroundMode())
			btn.setUsesTextLabel(True)
			btn.setTextPosition(QToolButton.Right)
			id = len(actions) - i - 1
			bg.insert(btn, id)
			btn.setName(actions[id][2])
			self._tools[name+actions[id][2]] = actions[id]
			# self.connect(btn, SIGNAL("toggled(bool)"), self.exclusiveSelect)
		
		w = QWidget(tbar)
		w.setBackgroundMode(tbar.backgroundMode())
		tbar.setStretchableWidget(w)
		
		tbox.addItem(tbar, name)
