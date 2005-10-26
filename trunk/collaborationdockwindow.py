# -*- coding: utf-8 -*-

from uiccollaborationwidget import *
from konzeptclient2 import *
from grapheditwindow import *
from qt import *

class CollaborationDockWindow(QDockWindow):
	""" user interface to the KonzeptClient """
	
	def __init__(self, parent = None, name = None):
		QDockWindow.__init__(self, parent, name)
		
		self.setResizeEnabled(True)
		self.setCloseMode(QDockWindow.Always)
		self.setFixedExtentWidth(260)
		self.setCaption("Collaboration")
		self._w = UicCollaborationWidget(self)
		self.setWidget(self._w)

		self.connect(self._w.connectBtn, SIGNAL('clicked()'), self.connectBtnClicked)
		self.connect(self._w.uploadBtn, SIGNAL('clicked()'), self.uploadBtnClicked)
		self.connect(self._w.downloadBtn, SIGNAL('clicked()'), self.downloadBtnClicked)
		self.connect(self._w.removeBtn, SIGNAL('clicked()'), self.removeBtnClicked)
		self.connect(self._w.editBtn, SIGNAL('clicked()'), self.editBtnClicked)
		
		self._parent = parent
		self._client = None
		self._connected = False
	
	def __del__(self):
		print "CollaborationDockWindow.__del__()"
		if self._client != None:
			self.clientDisconnect()
	
	def updatePrivateDocsListView(self, filePathList):
		self._w._privateDocsListView.clear()
		for fp in filePathList:
			fn = QFileInfo(fp).fileName()
			dirPath = QFileInfo(fp).dirPath()
			QListViewItem(self._w._privateDocsListView, fn, dirPath)
	
	def parent(self): return self._parent
	def client(self): return self._client
	
	def clientConnect(self):
		server = str(self._w.serverLineEdit.text())
		uname = str(self._w.uNameLineEdit.text())
		pwd = str(self._w.pwdLineEdit.text())
		if self._client != None:
			self._client.shutdown()
		self._client = KonzeptClient2(self, server)
		if self._client.connected(): self._client.login(uname, pwd)
		else: self._client = None
		
	def clientDisconnect(self):
		self._client.logoff()
		self._client.shutdown()
		self._client.join()
		self._client = None
		self._connected = False
		self._w.connectBtn.setText("Connect")
		self._w._usersListView.clear()
		self._w._sharedDocsListView.clear()
	
	def connectBtnClicked(self):
		print "self._connected = ", self._connected
		if not self._connected:
			self.clientConnect()
		else:
			self.clientDisconnect()
	
	def uploadBtnClicked(self):
		print "CollaborationDockWindow.uploadBtnClicked(): p0"
		if not self._connected: return
		item = self._w._privateDocsListView.selectedItem()
		print "CollaborationDockWindow.uploadBtnClicked(): p1"
		if item == None: return
		print "CollaborationDockWindow.uploadBtnClicked(): p2"
		fp = str(item.text(0))
		if item.text(1) != ".": fp = str(item.text(1)) + "/" + fp
		fn = str(QFileInfo(fp).fileName())
		doc = self._parent.documentByFilePath(fp)
		if doc == None:
			fp = str(item.text(1)) + "/" + str(item.text(0))
			return
		print "CollaborationDockWindow.uploadBtnClicked(): p3"
		self._client.documentUpload(fn, doc)
	
	def downloadBtnClicked(self):
		if not self._connected: return
		item = self._w._sharedDocsListView.selectedItem()
		if item == None: return
		fn = str(item.text(0))
		self._client.documentDownload(fn)
	
	def removeBtnClicked(self):
		if not self._connected: return
		item = self._w._sharedDocsListView.selectedItem()
		if item == None: return
		fn = str(item.text(0))
		self._client.documentRemove(fn)
	
	def editBtnClicked(self):
		if not self._connected: return
		item = self._w._sharedDocsListView.selectedItem()
		if item == None: return
		fn = str(item.text(0))
		self._client.editorOpen(fn)
	
	def event(self, e):
		if e.type() == KonzeptClient2.unableToConnect:
			QMessageBox.warning(self, "Konzept ", "Unable to connect to server.\n")
			self._client = None
			return True
		elif e.type() == KonzeptClient2.responseFromServer:
			rsp = e.data()
			if rsp["type"] == "login-ok":
				self._w.connectBtn.setText("Disconnect")
				self._connected = True
				QMessageBox.information(self, "Konzept ", "Login: OK.\n")
			elif rsp["type"] == "login-rejected":
				self.clientDisconnect()
				QMessageBox.warning(self, "Konzept ", "Login: Rejected.\n")
			elif rsp["type"] == "users-update":
				userStates =  rsp["userStates"]
				self._w._usersListView.clear()
				for userName in userStates:
					userName = userName.value()
					if userStates[userName] == 0: state = "offline"
					else: state = "online"
					QListViewItem(self._w._usersListView, userName, state)
			elif rsp["type"] == "documents-update":
				documents = rsp["documents"]
				self._w._sharedDocsListView.clear()
				for docName in documents:
					docName = docName.value()
					fn = documents[docName].fn()
					owner = documents[docName].owner()
					editor = documents[docName].editor()
					QListViewItem(self._w._sharedDocsListView, fn, owner, editor)
			elif rsp["type"] == "document-download":
				fp = str(qApp.applicationDirPath()) + "/" + rsp["fn"]
				w = GraphEditWindow(self._parent, fp, self._parent.workspace(), None, Qt.WDestructiveClose)
				w.graphEdit().setDocument(rsp["document"])
				w.show()
			elif rsp["type"] == "editor-open-ok":
				fp = "remote" + "/" + rsp["fn"]
				w = GraphEditWindow(self._parent, fp, self._parent.workspace(), None, Qt.WDestructiveClose)
				w.graphEdit().setDocument(rsp["document"])
				w.show()
			return True
		else:
			return QDockWindow.event(self, e)
