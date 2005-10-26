# -*- coding: UTF-8 -*-

from map import *
import md5
from socket import *
from messagebus import *
from serviceunit import *
from threading import *
from docinfo import *
from indentsink import *

# DEBUG
from sys import stdout

class KonzeptServer:
	""" The central connection accepting server thread.
	    A parallel multithreaded server architecture is used.
	    For each new client connection a new thread is forked. """
	
	acceptConnectionCmd = 0
	shutdownCmd = 1
	broadcastDocumentsUpdateCmd = 2
	
	# user states
	online = 1
	offline = 0
	
	def __init__(self, port = 50002):
		self._users = Map("users", Str, Str)             # uname -> hexdigest
		self._usersLock = Lock()
		self._userStates = Map()                         # uname -> {offline, offline}
		self._userStatesLock = Lock()
		self._documents = Map("documents", Str, DocInfo) # fn -> document info
		self._documentsLock = Lock()
		self._userDigests = Map("userDigests", Str, Str) # hexdigest -> uname
		self._openDocuments = Map()                      # fn -> instance of Document
		self._openDocumentsLock = Lock()
		self._editors = Map()                            # fn -> user name
		self._port = port
		self._cmdLock = Lock()                           # lock until a command is transmitted 
		                                                 # from a connection handler
		self._todoNext = KonzeptServer.acceptConnectionCmd
		self._msgBus = MessageBus()
		self._msgBus.start()
	
	def staticTypeName(): return "KonzeptServer"
	def typeName(self): return KonzeptServer.staticTypeName()
	staticTypeName = staticmethod(staticTypeName)
	def newInstance(): return KonzeptServer()
	newInstance = staticmethod(newInstance)
	
	def cmdLock(self): return self._cmdLock
	def port(self): return self._port
	
	def users(self): return self._users
	def usersLock(self): return self._usersLock
	def userStates(self): return self._userStates
	def userStatesLock(self): return self._userStatesLock
	def documents(self): return self._documents
	def documentsLock(self): return self._documentsLock
	def openDocuments(self): return self._openDocuments
	def openDocumentsLock(self): return self._openDocumentsLock
	
	def addUser(self, uname, pwd):
		hexdigest = md5.new(uname + pwd).hexdigest()
		self._users[hexdigest] = uname
		self._userDigests[uname] = hexdigests
	
	def delUser(self, uname):
		hexdigest = self._userDigests[uname]
		self._users.remove(uname)
		self._userDigests.remove(hexdigest)
	
	def setTodoNext(self, cmd): self._todoNext = cmd
	def todoNext(self): return self._todoNext
	
	def run(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.bind(('', self.port()))
		s.listen(20)
		while True:
			(conn, addr) = s.accept()
			if self.todoNext() == KonzeptServer.acceptConnectionCmd:
				# usual operation: create new thread for handling connection
				#ConnectionHandler(self, conn, addr)
				ServiceUnit(self, self._msgBus, conn, addr)
			else:
				# receive command from connection handling thread
				cmd = self.receiveCommand()
				if cmd == KonzeptServer.shutdownCmd:
					break
				self.setTodoNext(KonzeptServer.acceptConnectionCmd)
		s.close()
		for fn in self._openDocuments:
			self.syncToDisk(fn, self._openDocuments[fn])
		self._msgBus.shutdown()
		self._msgBus.join()
	
	# == transmitting commands from the connection handlers to the
	#    central connection accepting server
	
	def dummyConnect(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.connect(("127.0.0.1", self.port()))
		s.close()
	
	def transmitCommand(self, cmd):
		self.cmdLock().acquire()
		self.setTodoNext(cmd)
		self.dummyConnect()
	
	def receiveCommand(self):
		cmd = self.todoNext()
		self.cmdLock().release()
		return cmd
	
	# == high level interface for the connection handling threads
	
	def getUserName(self, hexdigest):
		if hexdigest in self._userDigests: return self._userDigests[hexdigest]
		else: return None
	
	def loginOk(self, userName):
		self._userStatesLock.acquire()
		self._userStates[userName] = KonzeptServer.online
		self._userStatesLock.release()
		
	def logoff(self, userName):
		self._userStatesLock.acquire()
		self._userStates[userName] = KonzeptServer.offline
		self._userStatesLock.release()
	
	def shutdown(self): self.transmitCommand(KonzeptServer.shutdownCmd)
	def broadcastDocumentsUpdate(self): self.transmitCommand(KonzeptServer.broadcastDocumentsUpdateCmd)
	
	def syncToDisk(self, fn, document):
		f = file(fn, 'w')
		sink = IndentSink(f)
		sink.write('<?xml version="1.0" standalone="yes" ?>\n')
		document.writeXml(sink)
		f.close()

	def addDocument(self, fn, ownerName, document):
		self.syncToDisk(fn, document)
		self._documentsLock.acquire()
		self._documents[fn] = DocInfo(fn, ownerName, None)
		self._documentsLock.release()
	
	def removeDocument(self, fn):
		self._documentsLock.acquire()
		self._documents.remove(fn)
		self._documentsLock.release()
		QFile.remove(fn)
	
	# == serialization interface
	
	def readXml(self, source, path = []):
		source.get("<%s>" % self.typeName())
		self._users = XmlFactory.instance(Map).createFromXml(source, path, initParams = ("users", Str, Str))
		self._documents = XmlFactory.instance(Map).createFromXml(source, path, initParams = ("documents", Str, DocInfo))
		source.get("</%s>" % self.typeName())
		for uname in self._users:
			self._userDigests[self._users[uname]] = uname
			self._userStates[uname] = KonzeptServer.offline
		self._documents.writeXml(IndentSink(stdout))
	
	def writeXml(self, sink):
		sink.write("<%s>\n" % self.typeName())
		self._users.writeXml(sink)
		self._documents.writeXml(sink)
		sink.write("</%s>\n" % self.typeName())

XmlFactory.instance(KonzeptServer).registerType(KonzeptServer)
