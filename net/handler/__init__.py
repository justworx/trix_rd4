#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ...util.sock.sockwrap import *


HANDLER_MAXIDLE = 300
HANDLER_BUFFER  = 4096


class Handler(sockwrap):
	"""
	Server connection handler; Default action: echo server.
	
	The default buffer size is 4096 bytes, which is much more than
	trix features typically need. In cases where a larger buffer size
	is needed, pass a handlerk keyword argument to the Server managing
	this connection. The handlerk value should be a dict containing
	any values needed by the Handler (or subclass) object handling
	to this connection.
	"""
	
	def __init__(self, sock, **k):
		"""
		Initialize basic Handler. Receives socket object and the stored
		Server configuration's "handlerk" dict, passed as kwargs.
		"""
		k.setdefault('buflen', HANDLER_BUFFER)
		
		# 
		# INIT
		#  - Receives a socket as produced by sockserv. DOES NOT store
		#    the socket here, but passes it to sockwrap, which passes it
		#    on to sockprop.
		#  - The sockprop class stores the actual socket object privately
		#    and exposes only a proxy to the socket (so as to prevent any
		#    chance of losing track of the socket and allowing it to stay
		#    open after the program exits.
		#
		#    REMEMBER...
		#  - DO NOT STORE the actual socket object anywhere but sockprop.
		#
		sockwrap.__init__(self, sock, **k)
		
		# defaults
		self.timeout = self.config.get('timeout', SOCK_TIMEOUT)
		
		# handler setup
		self.__maxidle = k.get('maxidle', HANDLER_MAXIDLE)
		self.__lastrecv = time.time()
	
	
	@property
	def maxidle(self):
		"""Max time server should wait before dropping connection."""
		return self.__maxidle
	
	@property
	def lastrecv(self):
		"""Time last data was received."""
		return self.__lastrecv
	
	@property
	def countdown(self):
		"""Time left until server shuts down this handler."""
		return self.maxidle - (time.time() - self.lastrecv)
	
	
	# HANDLE
	def handle(self):
		"""
		Receive and handle data. Default action is to 'echo'.
		"""
		try:
			data = self.socket.recv(self.buflen)
			if data:
				self.__lastrecv = time.time() # update for timeout
				self.handledata(data)
		except socket.timeout as ex:
			pass # Ignore Timeout
		except BaseException as ex:
			trix.log("Handler.handle FAIL!", 
				data=data, ex=type(ex).__name__, xargs=ex.args
			)
			raise
	
	
	# HANDLE DATA
	def handledata(self, data):
		"""
		OVERRIDE THIS METHOD!
		
		This method is a placeholder. You must override it to implent
		meaningful functionality (unless what you want is an echo server).
		"""
		if data:
			self.socket.send(data)

