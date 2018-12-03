#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.sock.sockserv import *
from ..util.runner import Runner
from .handler import Handler

SERVER_SLEEP = 0.1
SERVER_HANDLER = trix.innerpath('net.handler.Handler')


class Server(sockserv, Runner):
	"""Connection Server."""
	
	
	def __init__(self, config=None, **k):
		"""
		Start server. Pass config params for both Server and Runner.
		
		Pass config as a dict, url, address, or port, as required by the
		sockinfo.listen() classmethod.
		
		Minimum Required params:
		 - port
		
		Optional additional params:
		 # Server params
		 - backlog : max waiting connections. default: socket.SOMAXCONN
		 - host    : default: ''
		 - handler : A type or type desc. Eg, "trix.net.handler.Handler"
		 - nhandler: String spec, inner path. Eg, "net.handler.Handler"
		 - reuse   : True
		 
		 # Handler params
		 - maxidle : timeout for idle handler connections. default: 5m
		 - buflen  : handler recv buffer size. default: 4K
		 
		 # Runner params
		 - sleep   : sleep time after each loop. default: DEF_SLEEP, 0.1s
		 - cport   : url (or port) for local procserv connection
		"""
		
		#
		# The `config` argument may be anything accepted by the urlinfo 
		# class, with kwargs specifying any details such as sleep time. 
		# Alternately, config may be a dict containing at port and, 
		# optionally, any or all urlinfo, Server, and/or Runner params.
		#
		
		#
		# SET CONFIG DEFAULTS - MULTIPLE BASE CLASSES
		#  - Since this class has more than one base class, we need to be
		#    careful about the config.
		#  - This try block protects against loss of params if config is
		#    given as an int (port), tupel (host,port), or string (url)
		#    rather than as a dict.
		#  - Here we need to set only the defaults that are necessary to
		#    the sockserv class.
		#
		try:
			config.setdefault('backlog', socket.SOMAXCONN)
			config.setdefault('reuse', True)
		except AttributeError:
			k.setdefault('backlog', socket.SOMAXCONN)
			k.setdefault('reuse', True)
		
		#
		# SOCKSERV INIT
		#  - Binds and starts listening. This serves as a claim on the
		#    port, but nothing can really happen automatically unless 
		#    either the `run()` or `start()` methods is called.
		#  - However, the servers methods can be called manually; Use the
		#    sockserv methods (eg, `accept()`, `acceptif()`, etc...) if
		#    you want to handle the server functionality manually.
		#
		try:
			sockserv.__init__(self, config, **k)
			
			#
			# Now sockserv has a config that's potentially been updated with
			# params parsed from a url, so update config to match.
			# 
			config = self.config
			
		except Exception as ex:
			raise Exception(xdata(
					xerr=str(ex), args=str(ex.args), config=self.config)
				)
		
		#
		# NOTE
		#  - After this point, there's no need to send k along with config
		#    because k has already been applied (in the sockwrap init).
		#
		
		#
		# RUNNER INIT
		#  - Initialize runner but don't start running - that's up to the
		#    caller to do.
		#
		Runner.__init__(self, self.config)
		
		#
		# SET CONFIG DEFAULTS
		#  - Now self.config exists, so additional defaults may be set.
		#  - The server is already listening, but the defaults set here 
		#    are not strictly needed until `accept` is called. (Those 
		#    needed before this point are set above in the try/except
		#    block under the title "SET CONFIG DEFAULTS".)
		#
		self.config.setdefault('handler', SERVER_HANDLER)
		
		#
		# SET MEMBER VARIABLES
		#
		self.__handler = self._gethandlertype()
		self.__handlerk = self.config.get('handlerk', {})
		self.__handlers = []
		self.__remove = []
		
		# STATUS MESSAGES
		self.messages = []
		self.messageError = None
		self.iocount = 0
	
	
	
	
	#
	# DELETE
	#
	def __del__(self):
		try:
			self.stop()
		except:
			pass
			
		try:
			self.shutdown()
		except:
			pass
	
	
	
	
	#
	# PROPERTIES
	#
	@property
	def handler(self):
		"""Handler type."""
		return self.__handler
	
	@property
	def handlerk(self):
		"""Kwargs sent to new handlers when they're created."""
		try:
			return self.__handlerk
		except:
			self.__handlerk = {}
			return self.__handlerk
	
	@property
	def handlers(self):
		"""Handler-list items."""
		return self.__handlers
	
	@property
	def remove(self):
		"""Remove-list items"""
		
		# Handlers are added to this list when they time out, error out,
		# or need to be removed for whatever reason.
		return self.__remove
	
	
	
	
	#
	# STATUS
	#
	def status(self):
		r = Runner.status(self)
		status = dict(runner=r, server=dict(
			handler = self.handler,
			handlerk = self.handlerk,
			handlers = self.handlers, #len(self.handlers),
			iocount = self.iocount
		))
		if len(self.messages):
			status['messages'] = list(self.messages)
			self.messages = []
		if self.messageError:
			status['messageError'] = self.messageError
			self.messageError = None
		return status
	
	
	#
	# ACCEPT
	#
	def accept(self):
		"""Accept socket and return Handler."""
		s = sockserv.accept(self)
		h = self.__handler(s, **self.handlerk)
		self.addHandler(h)
	
	
	#
	#
	# ADD/REMOVE HANDLER
	#  - Always use addhandler to add handlers so that subclasses can
	#    perform any necessary processing.
	#
	#
	def addHandler(self, handler):
		"""Add `handler` to the active handler list."""
		#self.messages.append(["handler-add", handler])
		self.handlers.append(handler)
		self.messages.append(["handler-add", handler, handler.addr])
	
	def removeHandler(self, handler):
		"""Remove `handler` from the handler list."""
		#self.messages.append(["handler-remove", handler, handler.addr])
		addr = handler.addr
		self.handlers.remove(handler)
		self.messages.append(["handler-remove", handler, addr])
	
	
	#
	# GET HANDLER TYPE
	#
	def _gethandlertype(self):
		"""Utility for extracting the Handler type from config."""
		
		c = self.config
		
		#
		# The `handler` param may be given as a string describing a type
		# as given to `trix.create()`. The Handler type may also be given
		# using the `nhandler` param. In this case, it must be the string
		# path to an object defined inside the `trix` package.
		#
		x = c.get('nhandler')
		if x:
			#
			# If handler is passed by the nhandler param, it must be the
			# string path to an object created by trix.nvalue.
			#
			return trix.nvalue(x) 
		
		#
		# The `handler` param may be passed as a the string path to an
		# object or the type of the object.
		#
		x = c.get('handler', SERVER_HANDLER)
		if x:
			try:
				return trix.value(x) 
			except:
				# At this point, it'd better be a type...
				if not type(x) == type:
					raise ValueError ("err-handler-type", xdata(
						handler_type=type(x), require1=['str','type']
					))
				
				# It's a type!
				return x 
	
	
	#
	# RUNNER METHODS
	#  - Override runner methods to implement Server needs.
	#
	
	# DO NOT REMOVE THIS STUPID METHOD!
	def run(self):
		#
		# DO NOT REMOVE THIS!
		#  - Server won't start from __main__.py without this.. not 
		#    until I figure out how to dig into base classes for the
		#    method specified by `Process.launch`.
		#
		Runner.run(self)
	
	
	# IO
	def io(self):
		"""This method is called periodically when running.""" 
		
		# call inherrited io!
		Runner.io(self)
		
		if not self.socket:
			self.stop()
		
		else:
			remove = []
			
			# check for connection requests
			try:
				# accept any new socket connection
				conn, addr = self.socket.accept()
				
				# create a handler; add it to the list 
				handler = self.handler(conn, **self.handlerk)
				self.addHandler(handler)
				
				#print ("SERVER-DEBUG", self.handlerk)
				
			except socket.timeout:
				pass # ignore timeout
			
			# call `handle()` on each handler
			for h in self.handlers:
				if h.countdown < 0.0: 
					remove.append(h)
				else:
					try:
						h.handle()
					except BaseException as ex:
						try:
							self.messages.append([
								"handler-err", h, type(ex), ex.args, xdata()
							])
						except Exception as ex:
							#
							# TEMPORARY - TESTING/DEBUGGING
							#  - I'll keep this here for a while until I see that
							#    it's working (or until I realize there just can't
							#    be errors in something this simple).
							#
							self.messageError = xdata(xtype=type(ex), xargs=ex.args)
							pass
						finally:
							remove.append(h)
			
			# remove handlers marked for removal
			for r in remove:
				try:
					self.removeHandler(r)
				finally:
					r.shutdown()
					
			
			self.iocount += 1
			
			# SLEEP
			#  - sleep a bit (eg, 0.1 seconds)
			time.sleep(self.sleep)




