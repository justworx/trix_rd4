#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.runner import *
from ..net.connect import *


class Connection(Runner, Connect):
	"""Threadable single-connection runner."""
	
	def __init__(self, config=None, **k):
		"""Pass config params for Runner and Connect."""
		
		# get the config dict that calling sockcon would create
		self.__config = sockurl(config, **k).config
		
		# create the Runner portion of this object immediately
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
		Connect.__init__(self, self.__config)
		Runner.open(self)
		
		# perform any necessary connection procedures
		self.register()
		
	
	
	def register(self):
		pass
	
	
	
	def io(self):
		#
		# It's ok to override io() with a meaningless something-or-other
		# to ... i dunno... just do something... because Runner.io() is
		# absolutly blank. Does nothing - is just a placeholder. Right?
		#
		
		# actually, this probably should include a lineq
		r = self.read()
		if r:
			self.output(r.strip())
		
	
	
	def close(self):
		if self.active:
			try:
				Runner.close(self)
			except:
				pass
			try:
				Connect.shutdown(self)
			finally:
				pass
	
	
	
	def shutdown(self):
		self.close()
		Runner.stop(self)
	


