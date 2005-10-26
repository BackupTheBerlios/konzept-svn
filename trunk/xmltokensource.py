# -*- coding: UTF-8 -*-

from xml.sax import *
from xml.sax.xmlreader import *
from xml.sax.handler import *
from xml.sax.saxutils import *
from xml.sax.expatreader import *
from re import *
from sets import *
import sys

class XmlToken:
	startToken = 0
	endToken = 1
	charData = 2
	def __init__(self, type, value, lineNum = 0):
		self._type = type
		self._value = value
		self._lineNum = lineNum

	def type(self): return self._type
	def setType(self, type): self._type = type
	def value(self): return self._value
	def typeValue(self): return (self._type, self._value)

	def lineNum(self): return self._lineNum
	def setLineNum(self, lineNum): self._lineNum = lineNum

	def __eq__(self, b): return b.type() == self.type() and b.value() == self.value()
	def __ne__(self, b): return not self.__eq__(b)

	def __str__(self):
		if self._type == XmlToken.startToken: return "<"+self._value+">"
		elif self._type == XmlToken.endToken: return "</"+self._value+">"
		elif self._type == XmlToken.charData: return self.value()
		else: return None

	def isWhiteSpace(self):
		if self.type() != XmlToken.charData: return False
		return match(r"^\s*$", self.value()) != None

def tag(s):
	""" convenience function for creating a XmlToken object """
	mo = match(r"<(\w*)>", s)
	if mo != None:
		return XmlToken(XmlToken.startToken, mo.group(1))
	mo = match(r"</(\w*)>", s)
	if mo != None:
		return XmlToken(XmlToken.endToken, mo.group(1))
	return XmlToken(XmlToken.charData, s)

class SaxToTokenListContentHandler(ContentHandler):
	""" Translates SAX callbacks into a list of XmlToken.
	    Not applyable to XML documents containing attributes or
	    empty tags.
	"""
	def __init__(self):
		self._list = []
		self._locator = None

	def setDocumentLocator(self, locator):
		self._locator = locator
		#print locator

	def tokenList(self): return self._list

	def startElement(self, name, attributes):
		self._list.append(XmlToken(XmlToken.startToken, name, self._locator.getLineNumber()))

	def endElement(self, name):
		self._list.append(XmlToken(XmlToken.endToken, name, self._locator.getLineNumber()))

	def characters(self, content):
		# if match(r"^\s*$", content): return
		if len(self._list) != 0:
			if self._list[-1].type() == XmlToken.charData:
				self._list[-1] = XmlToken(XmlToken.charData, self._list[-1].value() + content, self._locator.getLineNumber())
				return
		self._list.append(XmlToken(XmlToken.charData, content, self._locator.getLineNumber()))

class XmlParseErrorHandler:
	def missingToken(self, lineNum, expectedToken):
		print str(lineNum) + ": Expected token", expectedToken, "."
		raise NotImplementedError("missingToken()")
	def unexpectedEndOfInput(self, lineNum, expectedToken):
		print str(lineNum) + ": Unexpected end of input, expected token", expectedToken, "."
		raise NotImplementedError("unexpectedEndOfInput()")

class XmlTokenSource(ContentHandler):
	""" Allows sequential reading of XML tokens.
	"""
	def __init__(self, charSource):
		#try:
			self._source = charSource
			self._valid = True
			self._errorHandler = XmlParseErrorHandler()
			
			contentHandler = SaxToTokenListContentHandler()
			if type(charSource) == str:
				parseString(charSource, contentHandler)
			else:
				reader = ExpatParser()
				reader.setContentHandler(contentHandler)
				reader.parse(charSource)
			self._tokenList = contentHandler.tokenList()
			#for e in self._tokenList:
			#	sys.stdout.write(str(e)+str(e.isWhiteSpace()))
			self._tokenListIndex = 0
		#except:
		#	self._valid = False
		#	print "Lex/Parser error!"

	def valid(self): return self._valid

	def eoi(self):
		if not self.valid(): return True
		return self._tokenListIndex >= len(self._tokenList)

	def __checkToken(self, token, expectedToken):
		if expectedToken.__class__ == str:
			expectedToken = tag(expectedToken)
		if expectedToken.__class__ == XmlToken:
			if token != expectedToken:
				self._errorHandler.missingToken(token.lineNum(), expectedToken)
		if expectedToken.__class__ == Set:
			if str(token) not in expectedToken:
				self._errorHandler.missingToken(token.lineNum(), expectedToken)

	def __skipWhiteSpace(self):
		""" skips all following character data tokens,
		    which contain only whitespace """
		while self._tokenList[self._tokenListIndex].isWhiteSpace():
			self._tokenListIndex = self._tokenListIndex + 1

	def get(self, expectedToken = None):
		""" Read next token.
		    Whitespace tokens are skipped if expectedTokens are given.
		"""
		if self.eoi():
			if expectedToken.__class__ != type(None):
				self._errorHandler.unexpectedEndOfInput(-1, expectedToken)
			return
		if expectedToken.__class__ != type(None): self.__skipWhiteSpace()
		token = self._tokenList[self._tokenListIndex]
		self._tokenListIndex = self._tokenListIndex + 1
		if expectedToken.__class__ != type(None): self.__checkToken(token, expectedToken)
		# print token.lineNum()
		return token

	def lookAhead(self, expectedToken = None):
		""" Delivers the next non-whitespace token.
		"""
		self.__skipWhiteSpace()
		token = self._tokenList[self._tokenListIndex]
		if expectedToken.__class__ != type(None): self.__checkToken(token, expectedToken)
		return token
