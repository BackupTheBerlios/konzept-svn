# -*- coding: UTF-8 -*-

class SetTrigger:
	def init(self, set):
		""" called by setTriggerHandler() to tell the trigger handler
		    which set it is working for """
		self._set = set

	def set(self): return self._set

	def add(self, set, e):
		""" called after element e is added to the set """
		None

	def remove(self, set, e):
		""" called after element e is removed from the set """
		None

	def unlink(self):
		""" called if the set is about destruction or if a different trigger handler is about becoming established """
		self._set = None
