# -*- coding: UTF-8 -*-

from list import *

class History:
	def __init__(self, ST, maxSteps = 50):
		""" ST ... state type
		"""
		self._maxSteps = maxSteps
		self._undoPos = None
		self._undoSteps = List("undoSteps", ST)
		self._redoSteps = List("redoSteps", ST)
		
	def append(self, state):
		self._redoSteps.removeAll()
		if self._undoSteps.count() == self._maxSteps:
			self._undoSteps.pop(0)
		self._undoSteps.append(state)
	
	def canUndo(self): return self._undoSteps.count() != 0
	def canRedo(self): return self._redoSteps.count() != 0
	
	def undo(self, currentState): 
		self._redoSteps.push(currentState)
		return self._undoSteps.pop()
	
	def redo(self, currentState): 
		self._undoSteps.push(currentState)
		return self._redoSteps.pop()
	
	def maxSteps(self): return self._maxSteps
