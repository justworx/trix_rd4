#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.

from ...util.runner import *
from ...net.connect import *
from .irc_event import *


class Connection(Connect, Runner):
	"""Threaded single-connection runner."""
	
	def __init__(self, config=None, **k):
		
		#
		# GAR! I need some way to set defaults, don't I?
		#      It has to be done before Connect is inited.
		#
		conf = sockconf(config, **k)
		
		# connect to remote socket
		Connect.__init__(self, conf, **k)
		
		# register connection here
		self.register(self)
		
		# start handling connection
		Runner.__init__(self, conf)
	
	
	def open(self):
		if not self.active:
			Connect.__init__(self, self.config, **k)
			self.register()
	
	def close(self):
		if self.active:
			Connect.shutdown(self)
			Runner.close(self)
	
	def register(self):
		pass
	
	
	
	
	
	
	@property
	def network(self):
		return self.config['network']
	
	@property
	def host(self):
		return self.config['host']
	
	@property
	def port(self):
		return self.config['port']
	
	@property
	def nick(self):
		return self.config['nick']
	
