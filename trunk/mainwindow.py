# -*- coding: utf-8 -*-

from uicmainwindow import *
from uicaboutdlg import *
from uicpageformatdlg import *
from uicgridlinesdlg import *

from grapheditwindow import *
from orderedset import *
from tooldockwindow import *
from collaborationdockwindow import *

from xmltokensource import *
from indentsink import *
from graph import *
from pageformatregistry import *
from qtdebug import *

from boxshape import *
from boxcolumnshape import *
from umlconnectorshape import *

class MainWindow(UicMainWindow):
	
	def __init__(self, parent = None, name = None, flags = 0):
		UicMainWindow.__init__(self, parent, name, flags)
		
		self.setAcceptDrops(True)
		self._workspace = QWorkspace(self)
		
		self.setCentralWidget(self._workspace)
		self.setCaption("Konzept")
		self.statusBar().message("Ready")
		
		self._currentDirPath = qApp.applicationDirPath()
		
		tw = ToolDockWindow(self)
		self._toolWindow = tw
		
		classShape1 = BoxShape(-30.0, -12.0, 30.0, 12.0)
		classShape1.setTextAlign(Qt.AlignHCenter | Qt.AlignVCenter)
		
		classShape2 = BoxColumnShape(-30.0, -12.0*2, 30.0, 12.0*2, 2)
		classShape2.column()[0].setTextAlign(Qt.AlignHCenter | Qt.AlignVCenter)
		classShape2.column()[1].setTextAlign(Qt.AlignLeft | Qt.AlignVCenter)
		
		classShape3 = BoxColumnShape(-30.0, -12.0*3, 30.0, 12.0*3, 3)
		classShape3.column()[0].setTextAlign(Qt.AlignHCenter | Qt.AlignVCenter)
		classShape3.column()[1].setTextAlign(Qt.AlignLeft | Qt.AlignVCenter)
		classShape3.column()[2].setTextAlign(Qt.AlignLeft | Qt.AlignVCenter)
		
		nodes = [("Class", "class1.png", "class1", QKeySequence(), classShape1),
		         ("Class (2)", "class2.png", "class2", QKeySequence(), classShape2),
		         ("Class (3)", "class3.png", "class3", QKeySequence(), classShape3)]
		
		connectors = [("Aggregation", "aggregation.png", "aggregation", QKeySequence(), UmlConnectorShape(Uml.aggregation)),
		              ("Composition", "composition.png", "composition", QKeySequence(), UmlConnectorShape(Uml.composition)),
		              ("Generalization", "generalization.png", "generalization", QKeySequence(), UmlConnectorShape(Uml.generalization)),
		              ("Implements", "implements.png", "implements", QKeySequence(), UmlConnectorShape(Uml.implements)),
		              ("Dependency", "dependency.png", "dependency", QKeySequence(), UmlConnectorShape(Uml.dependency)),
		              ("Association", "association.png", "association", QKeySequence(), UmlConnectorShape(Uml.association)),
		              ("Relation", "relation.png", "relation", QKeySequence(), UmlConnectorShape(Uml.relation))]
		
		tw.addGroup("Nodes", nodes)
		tw.addGroup("Edges", connectors)
		self.connect(tw, PYSIGNAL("selectionChanged"), self.toolSelectionChanged)
		self.setDockEnabled(tw, Qt.DockTop, False)
		self.setDockEnabled(tw, Qt.DockBottom, False)
		self.addDockWindow(tw, Qt.DockLeft)
		
		self._activeWindow = None
		self.connect(self._workspace, SIGNAL('windowActivated(QWidget*)'),
		             self.changeActiveWindow)
		 
		cw = CollaborationDockWindow(self)
		self._collabWindow = cw
		self.setDockEnabled(cw, Qt.DockTop, False)
		self.setDockEnabled(cw, Qt.DockBottom, False)
		self.addDockWindow(cw, Qt.DockRight)
		cw.hide()

	def workspace(self): return self._workspace
	
	def closeEvent(self, e):
		# ugly workaround for destructions never called
		# and destroy signal never delivered
		self._collabWindow.__del__()
		e.accept()
	
	def toolSelectionChanged(self):
		tw = self._toolWindow
		if self._activeWindow != None:
			if tw.selected("Nodes") != None:
				self._activeWindow.graphEdit().graph().setNodeShapePrototype(tw.selected("Nodes")[4])
			if tw.selected("Edges") != None:
				self._activeWindow.graphEdit().graph().setConnectorShapePrototype(tw.selected("Edges")[4])
	
	def toolRelease(self):
		self._toolWindow.unselect()
		if self._activeWindow == None: return
		self._activeWindow.graphEdit().graph().setNodeShapePrototype(None)
		self._activeWindow.graphEdit().graph().setConnectorShapePrototype(None)
	
	def changeActiveWindow(self, widget):
		self._activeWindow = widget
		if self._activeWindow != None:
			self._activeWindow.graphEdit().setActiveWindow()
			qApp.processEvents()
			self._activeWindow.graphEdit().setFocus()
			self.toolSelectionChanged()
	
	def documentOpened(self, wnd):
		l = self.filePathList()
		l.append(wnd.filePath())
		self._collabWindow.updatePrivateDocsListView(l)
	
	def documentClosed(self, wnd):
		l = self.filePathList()
		l.remove(wnd.filePath())
		self._collabWindow.updatePrivateDocsListView(l)

	def documentRenamed(self, wnd):
		self._collabWindow.updatePrivateDocsListView(self.filePathList())
	
	def filePathToWindow(self, filePath):
		for w in self._workspace.windowList(QWorkspace.CreationOrder):
			if w.filePath() == filePath:
				return w
		return None
	
	def filePathList(self):
		l = []
		for w in self._workspace.windowList(QWorkspace.CreationOrder):
			l.append(w.filePath())
		return l
	
	def documentByFilePath(self, fp):
		wnd = self.filePathToWindow(fp) 
		if wnd == None: return None
		return wnd.graphEdit().document()
	
	def fileNew(self):
		w = GraphEditWindow(self, None, self._workspace, None, Qt.WDestructiveClose)
		w.graphEdit().setGraph(Graph())
		w.graphEdit().setGrid(Grid(10))
		w.graphEdit().setPage(Page(A4, QPrinter.Landscape))
		w.show()
	
	def fileOpen(self):
		fn = QFileDialog.getOpenFileName(
			self._currentDirPath,
			"Konzept Graphs (*.kg);;Any (*.*)",
			self,
			"open file dialog",
			"Choose a file to open"
		)
		self._fileOpen(fn)
		
	def _fileOpen(self, fn):
		if fn == QString.null: return
		w = self.filePathToWindow(fn)
		if w != None:
			w.setFocus()
			return
		self._currentDirPath = QFileInfo(fn).dirPath()
		fn = str(fn)
		source = XmlTokenSource(file(fn))
		document = XmlFactory.instance(Document).createFromXml(source, [])
		w = GraphEditWindow(self, fn, self._workspace, None, Qt.WDestructiveClose)
		w.graphEdit().setDocument(document)
		w.show()
	
	def dragEnterEvent(self, e):
		if (QUriDrag.canDecode(e)): e.accept()
		else: e.ignore()
	
	def dropEvent(self, e):
		if (QUriDrag.canDecode(e)):
			files = QStringList()
			# files = []
			QUriDrag.decodeLocalFiles(e, files)
			for fn in files:
				self._fileOpen(fn);
	
	def __saveDocument(self, fn):
		sink = IndentSink(file(fn, "w+")) 
		sink.write('<?xml version="1.0" standalone="yes" ?>\n')
		ge = self._activeWindow.graphEdit()
		Document(ge.graph(), ge.page(), ge.grid()).writeXml(sink)

	def fileSave(self):
		if self._activeWindow == None: return

		fn = self._activeWindow.filePath()
		if fn == None:
			self.fileSaveAs()
		else:
			self.__saveDocument(fn)

	def fileSaveAs(self):
		if self._activeWindow == None: return
		
		fn = QFileDialog.getSaveFileName(
			self._activeWindow.filePath(),
			"Konzept Graphs (*.kg);;Any (*.*)",
			self,
			"save file dialog",
			"Choose a filename to save under"
		)
		if fn == QString.null: return
		self._currentDirPath = QFileInfo(fn).dirPath()
		if QFileInfo(fn).exists():
			result = QMessageBox.warning(
				self,
				str(self.caption()) + " - Warning",
				"A file named " + str(QFileInfo(fn).fileName()) + " already exists. "+
				"Are you sure you want to overwrite it?",
				"&Overwrite",
				"&Cancel"
			)
			if result == 1: return
		
		fn = str(fn)
		self._activeWindow.setFilePath(fn)
		self.__saveDocument(fn)

	def filePrint(self):
		if self._activeWindow == None: return
		
		printer = QPrinter(QPrinter.PrinterResolution)
		printer.setFullPage(True)
		printer.setOrientation(QPrinter.Landscape)
		if printer.setup():
			printer.newPage()
			painter = QPainter()
			painter.begin(printer)
			ge = self._activeWindow.graphEdit()
			ge.graph().unselectAll()
			ge.updateContents()
			ge.drawTo(painter)
			painter.end()

	def exportToSvg(self):
		if self._activeWindow == None: return
		
		fn = QFileDialog.getSaveFileName(
			self._currentDirPath,
			"Scalable Vector Graphics (*.svg);;Any (*.*)",
			self,
			"export file dialog",
			"Choose a filename to save under"
		)
		if fn == QString.null: return
		self._currentDirPath = QFileInfo(fn).dirPath()
		if QFileInfo(fn).exists():
			result = QMessageBox.warning(
				self,
				str(self.caption()) + " - Warning",
				"A file named " + str(QFileInfo(fn).fileName()) + " already exists. "+
				"Are you sure you want to overwrite it?",
				"&Overwrite",
				"&Cancel"
			)
			if result == 1: return
		pic = QPicture()
		painter = QPainter()
		painter.begin(pic)
		ge = self._activeWindow.graphEdit()
		ge.graph().unselectAll()
		ge.updateContents()
		ge.drawTo(painter)
		painter.end()
		pic.save(fn, "svg")

	def fileExit(self):
		"""result = QMessageBox.warning(
			self,
			self.caption() + " - Warning",
			"The graph has been modified.\n"+
			"Do you want to save it?",
			"&Save",
			"&Discard",
			"&Cancel"
		)"""
		self.close()

	def editCut(self):
		if self._activeWindow != None:
			self._activeWindow.graphEdit().ctrlX()
	
	def editCopy(self):
		if self._activeWindow != None:
			self._activeWindow.graphEdit().ctrlC()
			
	def editPaste(self):
		if self._activeWindow != None:
			self._activeWindow.graphEdit().ctrlV()
	
	def editUndo(self):
		if self._activeWindow != None:
			self._activeWindow.graphEdit().ctrlZ()
		
	def editRedo(self):
		if self._activeWindow != None:
			self._activeWindow.graphEdit().ctrlY()
	
	#def editFind(self):
	
	def settingsPageFormat(self):
		if self._activeWindow == None: return
		
		dlg = UicPageFormatDlg(self)
		dlg.pageFormatCombo.insertStringList(pageFormatRegistry.stringList())
		pg = self._activeWindow.graphEdit().page()
		dlg.pageFormatCombo.setCurrentItem(pageFormatRegistry.getIndex(pg.format()))
		if pg.orientation() == QPrinter.Landscape: 
			dlg.orientationCombo.setCurrentItem(0)
		else:
			dlg.orientationCombo.setCurrentItem(1)
		
		if dlg.exec_loop() == QDialog.Rejected: return
		
		if dlg.orientationCombo.currentItem() == 0:
			o = QPrinter.Landscape
		else:
			o = QPrinter.Portrait
		fmt = pageFormatRegistry[dlg.pageFormatCombo.currentItem()]
		pg = Page(fmt, o)
		self._activeWindow.graphEdit().setPage(pg) 
		self._activeWindow.graphEdit().updateContents()
	
	def settingsGridLines(self):
		if self._activeWindow == None: return
		
		ge = self._activeWindow.graphEdit()
		dlg = UicGridLinesDlg(self)
		
		if ge.grid() == None:
			dlg.spinBox.setValue(Grid.defaultRasterSize_mm)
			dlg.checkBox.setOn(False)
		else:
			dlg.spinBox.setValue(ge.grid().rasterSize_mm())
			dlg.checkBox.setOn(True)
		
		if dlg.exec_loop() == QDialog.Rejected: return
		
		if dlg.checkBox.isOn():
			ge.setGrid(Grid(dlg.spinBox.value()))
		else:
			ge.setGrid(None)
			
		ge.updateContents()
	
	def helpAbout(self):
		UicAboutDlg(self).exec_loop()
