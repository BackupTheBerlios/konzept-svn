# -*- coding: utf-8 -*-

from socketadapter import *
from messageprocessor import *
from threading import *
from socket import *
from qt import *
import md5

# for type registration
from document import *
from boxshape import *
from boxcolumnshape import *
from umlconnectorshape import *
from docinfo import *

# DEBUG
from sys import stdout
from indentsink import *

class KonzeptClient2:

	# event for GUI control
	unableToConnect = 1001
	responseFromServer = 1002
	
	def __init__(self, guiControl, serverAddr):
		self._guiControl = guiControl
		self._serverAddr = serverAddr
		try:
			self._socket = socket(AF_INET, SOCK_STREAM)
			self._socket.connect((serverAddr, 50002))
		except:
			qApp.postEvent(self._guiControl, QCustomEvent(KonzeptClient2.unableToConnect))
			self._socket = None
			return
		self._socketAdapter = SocketAdapter(self._socket)
		self._responseProcessor = MessageProcessor()
		self._responseProcessor.process = self.responseProcessor_process
		self._responseProcessor.connect(self._socketAdapter)
		self._socketAdapter.start()
		self._responseProcessor.start()
	
	def connected(self):
		return self._socket != None
		
	def serverAddr(self): return self._serverAddr
	
	def login(self, userName, pwd):
		rq = Message()
		rq["type"] = "login"
		rq["hexdigest"] = md5.new(userName + pwd).hexdigest()
		self._socketAdapter.send(rq)
	
	def logoff(self):
		rq = Message()
		rq["type"] = "logoff"
		self._socketAdapter.send(rq)
	
	def documentUpload(self, fn, doc):
		rq = Message()
		rq["type"] = "document-upload"
		rq["fn"] = fn
		rq["document"] = doc
		self._socketAdapter.send(rq)

	def documentDownload(self, fn):
		rq = Message()
		rq["type"] = "document-download"
		rq["fn"] = fn
		self._socketAdapter.send(rq)
		
	def documentRemove(self, fn):
		rq = Message()
		rq["type"] = "document-remove"
		rq["fn"] = fn
		self._socketAdapter.send(rq)
		
	def editorOpen(self, fn):
		rq = Message()
		rq["type"] = "editor-open"
		rq["fn"] = fn
		self._socketAdapter.send(rq)
	
	def responseProcessor_process(self, rsp):
		# DEBUG
		rsp.writeXml(IndentSink(stdout)) 
		qApp.postEvent(self._guiControl, QCustomEvent(KonzeptClient2.responseFromServer, rsp))
	
	def shutdown(self):
		print "self._responseProcessor.shutdown()"
		self._responseProcessor.shutdown()
		print "self._socketAdapter.shutdown()"
		self._socketAdapter.shutdown()
		print "done."

	def join(self):
		print "self._socketAdapter.join()"
		self._socketAdapter.join()
		print "self._responseProcessor.join()"
		self._responseProcessor.join()
