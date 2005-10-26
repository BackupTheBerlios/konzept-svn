# -*- coding: utf-8 -*

from threading import *

class MessageProcessor(Thread):
	""" waits for messages delivered, processes them
	    and waits again...
	"""

	def __hash__(self): return object.__hash__(self)
	def __cmp__(self, b): return self.__hash__() - b.__hash__()
	
	def __init__(self, maxQueueLen = 2): 
		""" private method """
		Thread.__init__(self)
		self._msgQueue = []
		self._msgQueueLock = Lock()
		self._empty = Semaphore(maxQueueLen)
		self._full = Semaphore(0)
		self._goingDown = False
		self._medias = []
		self._mediasLock = Lock()
	
	def run(self):
		""" private method """
		while not self._goingDown:
			print "MessageProcessor.run(): self._full.acquire()"
			self._full.acquire()
			if self._goingDown: break
			self._msgQueueLock.acquire()
			msg = self._msgQueue.pop()
			self._msgQueueLock.release()
			self.process(msg)
			print "MessageProcessor.run(): self._empty.release()"
			self._empty.release()
		
		print "MessageProcessor.run(): terminated."
	
	def connect(self, media):
		""" connect this message processor to a certain
		    message transmission media """
		self._mediasLock.acquire()
		self._medias.append(media)
		self._mediasLock.release()
		media.connect(self)
	
	def disconnect(self, media):
		""" disconnect this message processor from a certain
		    message transmission media """
		self._mediasLock.acquire()
		self._medias.remove(media)
		self._mediasLock.release()
		media.disconnect(self)
	
	def unlink(self):
		""" disconnect from all message transmission medias """
		print "MessageProcessor.unlink(): self._mediasLock.acquire()"
		self._mediasLock.acquire()
		print "MessageProcessor.unlink(): p0"
		for media in self._medias:
			print "disconnect from ", media
			media.disconnect(self)
		self._medias = []
		print "MessageProcessor.unlink(): self._mediasLock.release()"
		self._mediasLock.release()
	
	def deliver(self, msg):
		""" called from outside to deliver messages """
		print "MessageProcessor.deliver(): self._empty.acquire()"
		self._empty.acquire()
		self._msgQueueLock.acquire()
		self._msgQueue.append(msg)
		self._msgQueueLock.release()
		print "MessageProcessor.deliver(): self._full.release()"
		self._full.release()
	
	def send(self, media, msg):
		""" transmit a message over connected media """
		media.send(msg)
	
	def process(self, msg):
		""" message procession method """
		print "MessageProcessor.process(): Not implemented yet"
	
	def shutdown(self):
		print "MessageProcessor.shutdown(): self.unlink()"
		self.unlink()
		print "MessageProcessor.shutdown(): done."
		self._goingDown = True
		self._full.release()
	
