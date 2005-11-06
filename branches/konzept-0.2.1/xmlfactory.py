# -*- coding: UTF-8 -*-

from sets import *

class XmlTypeInfo:
	def __init__(self, newInstance, readXml):
		self.newInstance = newInstance
		self.readXml = readXml
	
class XmlFactory:
	""" Type based template class for a set of factories.
	    Each factory singleton XmlFactory.instance(creationType) creates
	    objects from an XML text of type creationType.
	"""

	_instance = {}

	def instance(abstractProduct):
		if abstractProduct not in XmlFactory._instance:
			XmlFactory._instance[abstractProduct] = XmlFactory(abstractProduct)
		return XmlFactory._instance[abstractProduct]

	instance = staticmethod(instance)

	def __init__(self, abstractProduct):
		""" private constructor """
		self._abstractProduct = abstractProduct
		self._types = {}
		self._startTags = Set()
		self.instance = XmlFactory.instance

	def abstractProduct(self): return self._abstractProduct
	def registeredTypes(self): return self._typeNameToStartTag.values()
	
	def registerType(self, classObj):
		if self._abstractProduct != None:
			XmlFactory.instance(None).registerType(classObj)
		
		typeName = classObj.staticTypeName()
		e = XmlTypeInfo(classObj.newInstance, classObj.readXml)
		self._types[typeName] = e
		self._startTags.add("<%s>" % typeName)

	def createFromXml(self, source, path, initParams = None, readParams = None):
		token = source.lookAhead(self._startTags)
		e = self._types[token.value()]
		if initParams == None:
			obj = e.newInstance()
		else:
			obj = e.newInstance(initParams)
		if readParams == None:
			e.readXml(obj, source, path)
		else:
			e.readXml(obj, source, path, readParams)
		return obj
