# -*- coding: utf-8 -*

from threading import *

class ConnectionAcceptor(Thread):
	def __init__(self, ls, msgProcessorType, msgBus):
		Thread.__init__(self)
		self._socket = ls
		self._msgProcessorType = msgProcessorType
		self._msgBus = msgBus
		self._goingDown = False
	
	def run(self):
		while not self._goingDown:
			try:
				cs = self._socket.accept()
			except:
				if not self._goingDown:
					self.acceptError()
			if not self._goingDown:
				msgProcessor = self._msgProcessorType(cs)
				msgProcessor.connect(self._msgBus)
	
	def acceptError(self):
		print "ConnectionAcceptor.acceptError(): Not implemented yet"
	
	def shutdown(self):
		self._goingDown = True
		self._socket.close()
