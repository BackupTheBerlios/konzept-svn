# -*- coding: UTF-8 -*-

from socketadapter import *
from messageprocessor import *
from message import *
from list import *
from atomics import *

from xmlfactory import *
from xmltokensource import *

# for type registration
from document import *
from boxshape import *
from boxcolumnshape import *
from umlconnectorshape import *

# DEBUG
from sys import stdout
from indentsink import *

class ServiceUnit:
	def __init__(self, server, msgBus, socket, remoteAddr):
		self._server = server
		self._msgBus = msgBus
		self._socket = socket
		self._remoteAddr = remoteAddr
		self._userName = None
		self._requestProcessor =  MessageProcessor()
		self._requestProcessor.setDaemon(True)
		self._requestProcessor.process = self.requestProcessor_process
		self._socketAdapter = SocketAdapter(socket)
		self._socketAdapter.setDaemon(True)
		self._socketAdapter.ioError = self.socketAdapter_ioError
		self._requestProcessor.connect(self._socketAdapter)
		self._requestProcessor.connect(self._msgBus)
		self._requestProcessor.start()
		self._socketAdapter.start()
		print "Connection established: %s" % str(self._remoteAddr)
	
	def broadcastUsersUpdate(self):
		bm = Message()
		bm["type"] = "users-update"
		bm["userStates"] = self._server.userStates()
		self._msgBus.broadcast(bm)
		
	def broadcastDocumentsUpdate(self):
		bm = Message()
		bm["type"] = "documents-update"
		bm["documents"] = self._server.documents()
		self._msgBus.broadcast(bm)
	
	def requestProcessor_process(self, rq):
		# DEBUG
		print "ServiceUnit.requestProcessor_process(): p0"
		rq.writeXml(IndentSink(stdout)) 
		
		if rq["type"] == "login":
			rsp = Message()
			self._userName = self._server.getUserName(rq["hexdigest"])
			if self._userName  != None:
				rsp["type"] = "login-ok"
				self._socketAdapter.send(rsp)
				self._server.loginOk(self._userName)
				self.broadcastUsersUpdate()
				self.broadcastDocumentsUpdate()
			else:
				rsp["type"] = "login-rejected"
				self._socketAdapter.send(rsp)
				self.shutdown()
		elif rq["type"] == "logoff":
			self.shutdown()
		elif rq["type"] == "shutdown":
			self.shutdown()
			self._server.shutdown()
		elif rq["type"] == "users-update":
			self._server.userStatesLock().acquire()
			self._socketAdapter.send(rq)
			self._server.userStatesLock().release()
		elif rq["type"] == "documents-update":
			self._server.documentsLock().acquire()
			self._socketAdapter.send(rq)
			self._server.documentsLock().release()
		elif rq["type"] == "document-upload":
			fn = rq["fn"]
			doc = rq["document"]
			self._server.addDocument(fn, self._userName, doc)
			self._server.openDocumentsLock().acquire()
			if fn in self._server.openDocuments():
				self._server._openDocuments[fn] = doc
			self._server.openDocumentsLock().release()
			self.broadcastDocumentsUpdate()
		elif rq["type"] == "document-download":
			self._server.documentsLock().acquire()
			b = rq["fn"] in self._server.documents()
			self._server.documentsLock().release()
			if b:
				fn = rq["fn"]
				rsp = Message()
				rsp["type"] = "document-download"
				rsp["fn"] = fn
				self._server.openDocumentsLock().acquire()
				if not fn in self._server.openDocuments():
					doc = self.loadDocument(fn)
					self._server._openDocuments[fn] = doc
				else:
					doc = self._server._openDocuments[fn]
				self._server.openDocumentsLock().release()
				rsp["document"] = doc
				self._socketAdapter.send(rsp)
		elif rq["type"] == "document-remove":
			self._server.documentsLock().acquire()
			b = rq["fn"] in self._server.documents()
			self._server.documentsLock().release()
			if b:
				self._server.removeDocument(rq["fn"])
				self.broadcastDocumentsUpdate()
		elif rq["type"] == "editor-open":
			self._server.documentsLock().acquire()
			b = rq["fn"] in self._server.documents()
			self._server.documentsLock().release()
			if b:
				fn = rq["fn"]
				self._server.openDocumentsLock().acquire()
				if not fn in self._server.openDocuments():
					doc = self.loadDocument(fn)
					self._server._openDocuments[fn] = doc
				else:
					doc = self._server._openDocuments[fn]
				self._server.openDocumentsLock().release()
				rsp = Message()
				rsp["type"] = "editor-open-ok"
				rsp["fn"] = fn
				rsp["document"] = doc
				self._socketAdapter.send(rsp)
		elif rq["type"] == "editor-document-update":
			fn = rq["fn"]
			doc = rq["document"]
			self._server.openDocumentsLock().acquire()
			if fn in self._server.openDocuments: 
				self._server._openDocuments[fn] = doc
			self._server.openDocumentsLock().release()
		else:
			None # unknow request

	def loadDocument(self, fn):
		f = file(fn)
		source = XmlTokenSource(fn)
		document = XmlFactory.instance(Document).createFromXml(source, [])
		f.close()
		return document
	
	def socketAdapter_ioError(self):
		print "ServiceUnit.socketAdapter_ioError()"
		self.shutdown()
	
	def shutdown(self):
		print "ServiceUnit.shutdown() ..."
		if self._userName != None:
			self._server.logoff(self._userName)
			self.broadcastUsersUpdate()
		print "self._requestProcessor.shutdown()"
		self._requestProcessor.shutdown()
		print "self._socketAdapter.shutdown()"
		self._socketAdapter.shutdown()
		print "Connection closed: %s" % str(self._remoteAddr)
