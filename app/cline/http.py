#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from . import *
from ...util.urlinfo import *

class http(cline):
	"""
	Run a test web server. Use Ctrl-c to stop.
	
	This command will create and run a temporary Server object. The 
	`net.handler.hhttp.HandleHttp` handler is the default, but any
	object that handles http requests may be substituted setting the
	--handler or --nhandler keyword arguments.
	
	Example - Using nhandler:
	python3 -m trix http --nhandler=net.handler.htest.HTest
	
	Assuming you're developing a web service handler *outside* the trix
	package directory structure, you'll probably want to use the handler
	keyword argument instead.
	
	Example - Using 'handler':
	python3 -m trix http --handler=yourcode.yourclass.YourHandler
	
	Other Examples:
	# By default, the server will run on port 8888:
	python3 -m trix http
	
	# For a web server on a different port:
	python3 -m trix http 8080
	
	# To see debug messages after closing the command, pass the -d flag:
	python3 -m trix http -d
	"""
	
	DefPort = 8888
	
	def __init__(self):
		
		cline.__init__(self)
		
		# config may be given as a url or port
		config = self.args[0] if self.args else {}
		
		if config:
			try:
				# in case config was given as a port, make it an int
				config = int(config)
			except:
				# Otherwise, the argument must be a string url, which will
				# be parsed below.
				pass
			
			config = urlinfo(config).dict
		
		# kwargs must update the config
		config.update(self.kwargs)
		
		# set defaults...
		if not 'port' in config:
			config['port'] = self.DefPort
		
		# for display (Open: link)...
		config.setdefault('host', 'localhost')
		if not config['host']:
			config['host'] = 'localhost'
		
		# These are here to make the displayed url look (and work) right
		# even if they were not explicitly specifically given.
		config.setdefault('scheme', 'http')
		config.setdefault('nhandler', 'net.handler.hhttp.HandleHttp')
		
		# create the server
		s = trix.ncreate('net.server.Server', config)
		
		try:
			print ("HTTP Server running on port: %i" % s.port) 
			print ("Open: %s" % s.url)
			print ("Use Ctrl-c to stop.")
			s.run()
		except KeyboardInterrupt:
			s.shutdown()
			print ("Server shutdown.")
		
		# display debug messages after server stops
		if ('d' in self.flags):
			s.display()

