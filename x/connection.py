#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.runner import *
from ..net.connect import *


class Connection(Runner):
	"""Threadable single-connection runner."""
	
	def __init__(self, config=None, **k):
		"""Pass config params for Runner and Connect."""
		Runner.__init__(self, config, **k)
		self.__connect = None
	
	
	def open(self):
		"""
		Opens a connection and calls the `register()` method. If the
		connection requires some sort of retistration or negotiation,
		it must be handled in by the register method.
		
		This method will fail if the connection is already open. Call
		close first if you want to reconnect.
		"""
		# raise an error if already open
		if self.active:
			raise Exception('already-open')
		
		# create a Connect based on config provided to init
		self.__connect = Connect(self.config)
		Runner.open(self)
		
		# perform any necessary connection procedures
		self.register()
		
	
	
	def register(self):
		pass
	
	
	
	def io(self):
		# I2t's ok to override io() with a meaningless something-or-other
		# to ... i dunno... just do something... because Runner.io() is
		# absolutly blank. Does nothing - is just a placeholder. Right?
		r = self.__connect.read()
		if r:
			self.output(r.strip())
		
	
	
	def close(self):
		if self.active or self.__connect:
			try:
				self.__connect.shutdown()
				del(self.__connect)
			finally:
				self.__connect = None
			
			


