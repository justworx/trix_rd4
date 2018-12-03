#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .hlines import *


class HandleSockIO(HandleLines):
	"""Handler for socket connection servers."""
	
	def __init__(self, *a, **k):
		"""
		Kwargs must include a callback method, function, or lambda.
		"""
		HandleLines.__init__(self, *a, **k)
		self.callback = k['callback']
	
	
	def handledata(self, data):
		"""
		Queue new data then handle all available input.
		"""
		HandleLines.handledata(self, data)
		self.handleio()
	
	
	def handleio(self):
		"""Send commands or data to the trix app; return any results."""
		for data in self.lineq.lines:
			r = self.callback(data)
			if r:
				if r[-2:] != self.lineq.newl:
					r = r + self.lineq.newl
				self.write(r)
				
	

