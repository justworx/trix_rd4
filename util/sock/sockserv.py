#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from . import *
from ._sockurl import *
from ._sockprop import *

class sockserv(sockurl, sockprop):
	"""Socket server; basic server connection features.	"""
	
	def __init__(self, config=None, **k):
		"""
		Pass params defining url, backlog, options, and socket.
		 - Anything parsable by urlinfo may be given as the config.
		 - Include server params (eg, opts, backlog, etc...).
		 - Socket params 'family', 'type', and 'proto' are honored. 
		"""
		
		#
		# Handle config first. The sockurl constructor does this as is
		# needed by sockserv - by honoring either:
		#  * a dict with all URL and Server-related parameters, or...
		#  * acceptable url arguments (string, tuple, int) for creation
		#    of a url dict to use as config.
		# 
		# Since `k` is always applied, both of these options should work
		# equally well.
		# 
		
		#
		# SERVER CONFIG
		#  - sockurl will create the server config dict, exposed by 
		#    sockconf as self.config.
		#
		sockurl.__init__(self, config, **k)
		
		#
		# CREATE LISTENING SOCKET
		#  - Create a *listening* server socket.
		#  - Pass the socket object directly to sockprop, which will store
		#    the only copy of the exact socket object reference securely
		#    and will share a proxy to the socket via its socket property.
		#    This will - hopefully - prevent the socket from remaining in
		#    memory after the program exits.
		#
		#    REMEMBER...
		#  - DO NOT STORE the actual socket object anywhere but sockprop.
		#
		sockprop.__init__(self, self.listen())
	
	
	def __del__(self):
		try:
			self.__sock.shutdown(SHUT_RDWR)
		except:
			pass
	
	
	def accept(self):
		"""Return self.socket.accept()"""
		return self.socket.accept()
	
	
	def acceptif(self):
		"""Accept and return the next waiting connection, or None."""
		try:
			return self.accept()
		except socket.timeout:
			return None
	
	
	def listen(self):
		"""Create a server socket as configured, bind, and listen."""
		
		c = self.config
		u = self.url
		
		# Socket Creation Params
		cfamily = trix.value("socket", c.get('family', 'AF_INET'))
		ctype = trix.value("socket", c.get('type', 'SOCK_STREAM'))
		cproto = trix.value("socket", c.get('proto')) or 0
		
		# CREATE SOCKET
		self.__sock = socket.socket(cfamily, ctype, cproto)
		s = trix.proxify(self.__sock)
		
		#
		# WRAP SERVER SOCKET
		#  - I don't know how to do this, let alone test it. Hopefully 
		#    this works for people with a certificate somewhere.
		#  - Any comments/advice would be welcome.
		#
		if c.get('wrap'):
			s = trix.module('ssl').wrap_socket(s, server_side=True)
		
		#
		# TIMEOUT
		#  - Servers get a very small timeout; if there's no connection
		#    waiting, the Server class goes to sleep for a short while.
		#
		s.settimeout(c.get('timeout', SOCK_TIMEOUT))
		
		# SOCKET OPTIONS
		opts = c.get('options', [])
		if c.get('reuse', True):
			opts.append((socket.SOL_SOCKET, socket.SO_REUSEADDR, 1))
		
		for opt in opts:
			s.setsockopt(*opt)
		
		# BIND (to address)
		s.bind((
			c.get('host', ''),      # default: available interfaces
			c.get('port', 0) or 0   # required
		))
		
		# LISTEN (for incoming connections)
		s.listen(c.get('backlog', socket.SOMAXCONN))
		
		# store, for deletion when object deconstructs
		return s




