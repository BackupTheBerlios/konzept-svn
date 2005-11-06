# -*- coding: utf-8 -*

from threading import *

class MessageMedia(Thread):
	""" abstract base class for all message medias """
	
	def __init__(self):
		Thread.__init__(self)
		self._receivers = []
		self._receiversLock = Lock()

	def connect(self, receiver):
		self._receiversLock.acquire()
		self._receivers.append(receiver)
		self._receiversLock.release()
	
	def disconnect(self, receiver):
		self._receiversLock.acquire()
		self._receivers.remove(receiver)
		self._receiversLock.release()
	
	def broadcast(self, msg):
		print "MessageMedia.broadcast(): self._receiversLock.acquire()"
		self._receiversLock.acquire()
		listCopy = self._receivers[:]
		print "MessageMedia.broadcast(): self._receiversLock.release()"
		self._receiversLock.release()
		for receiver in listCopy:
			print "MessageMedia.broadcast(): receiver.deliver(msg)"
			receiver.deliver(msg)

	def broadcastShutdown(self):
		self._receiversLock.acquire()
		for receiver in self._receivers:
			receiver.shutdown()
		self._receiversLock.release()
