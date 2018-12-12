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
		if config:
			if isinstance(config, dict):
				config.update(k)
				config.setdefault('encoding', DEF_ENCODE)
				self.config = config
			else:
				# if config is not given by dict, it must be a url
				k.setdefault('encoding', DEF_ENCODE)
		
		Runner.__init__(self, config, **k)
	
	
	
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
		
		Connect.__init__(self, self.config)
		Runner.open()
		
		# 
		self.register()
		
	
	
	def register(self):
		pass
	
	
	
	def io(self):
		# I2t's ok to override io() with a meaningless something-or-other
		# to ... i dunno... just do something... because Runner.io() is
		# absolutly blank. Does nothing - is just a placeholder. Right?
		pass



