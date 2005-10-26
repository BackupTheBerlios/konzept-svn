# -*- coding: utf-8 -*

from messagemedia import *
from message import *

class SocketAdapter(MessageMedia):
	def __init__(self, socket):
		MessageMedia.__init__(self)
		self._socket = socket
		self._goingDown = False
	
	def run(self):
		while not self._goingDown:
			msg = Message()
			n = 0
			#try:
			n = msg.readFrame(self._socket)
			#except:
			#	if not self._goingDown:
			#		self.ioError()
			print n
			if self._goingDown: break
			if n == 0:
				msg.removeAll()
				msg["type"] = "connection-closed"
				self.broadcast(msg)
				self.shutdown()
			else:
				self.broadcast(msg)
		print "SocketAdapter.run(): terminated."
	
	def send(self, msg):
		#try:
		msg.writeFrame(self._socket)
		#except:
		#	if not self._goingDown:
		#		self._errorHandler.ioError(self)

	def ioError(self):
		print "SocketAdapter.ioError(): Not implemented yet"

	def shutdown(self):
		if self._goingDown == False:
			self._goingDown = True
			#try:
			self._socket.shutdown(2)        # unblocks run()!
			#except:
			#	None

