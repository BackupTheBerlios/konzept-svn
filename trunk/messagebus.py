# -*- coding: utf-8 -*

from messagemedia import *
from threading import *

class MessageBus(MessageMedia):
	def __init__(self):
		MessageMedia.__init__(self)
		self._msgQueue = []
		self._msgQueueLock = Lock()
		self._full = Semaphore(0)
		self._empty = Semaphore(2)
		self._goingDown = False
	
	def run(self):
		while not self._goingDown:
			print "MessageBus.run(): self._full.acquire()"
			self._full.acquire()
			if not self._goingDown:
				self._msgQueueLock.acquire()
				(receiver, msg) = self._msgQueue.pop()
				self._msgQueueLock.release()
				if receiver != None:
					receiver.deliver(msg)
				else:
					MessageMedia.broadcast(self, msg)
			print "MessageBus.run(): self._empty.release()"
			self._empty.release()
	
	def send(self, receiver, msg):
		print "MessageBus.send(): self._empty.acquire()"
		self._empty.acquire()
		self._msgQueueLock.acquire()
		self._msgQueue.append((receiver, msg))
		self._msgQueueLock.release()
		print "MessageBus.send(): self._full.release()"
		self._full.release()

	def broadcast(self, msg):
		self.send(None, msg)
	
	def shutdown(self):
		# self.unlink()
		print "MessageBus.shutdown()"
		self._goingDown = True
		self.send(None, None)
