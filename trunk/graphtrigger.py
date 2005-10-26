# -*- coding: UTF-8 -*-

class GraphTrigger:
	
	def stateChanged(self, graph):
		print "GraphTrigger.stateChanged()"
	
	def beforeModified(self, graph):
		print "GraphTriggerHandler.beforeModified()"
	
	def modified(self, graph):
		print "GraphTriggerHandler.modified()"
