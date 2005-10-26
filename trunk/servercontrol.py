# -*- coding: UTF-8 -*-

from uicservercontrol import *
from socket import *
from message import *

class ServerControl(UicServerControl):
	def __init__(self, parent = None, name = None):
		UicServerControl.__init__(self, parent, name)
		
		self.connect(self.shutdownBtn, SIGNAL("clicked()"),
		             self.shutdownBtnClicked)
	
	def shutdownBtnClicked(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.connect(("127.0.0.1", 50002))
		
		om = Message()
		om["type"] = "shutdown"
		om.writeFrame(s)
		
		#s.close()
