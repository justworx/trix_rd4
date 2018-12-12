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
		
		# connect to remote socket
		Connect.__init__(self, config, **k)
		
		# register connection here
		self.register(self)
		
		# start handling connection
		Runner.__init__(self, self.config)
		
		#
		# Set active to true since Connect aspect of the object is now
		# connected. Subsequent calls to `open` will hit this object's
		# `open` method.
		#
		Runner.open(self)
		
		# Start managing (running) the connection.
		if self.config.get("auto") == 'run':
			self.run()
		elif self.config.get('auto', True) == 'start':
			self.start()
	
	
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
	
	
	
	def register(self):
		pass
	
	
	
	def open(self):
		if not self.active:
			Connect.__init__(self, config, **k)
	
	
	
