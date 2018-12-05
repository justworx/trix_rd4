#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.enchelp import * # trix
from ..util.xthread import *
from ..util.stream.buffer import *
from .output import *

DEF_SLEEP = 0.1


class Runner(Output):
	"""
	Start, manage, and stop a (possibly threaded) event loop. Override
	the `io` method to define actions that must be taken each pass 
	through the loop.
	
	NOTE:
	 - Always use base-class `Output` methods `write` and `writeline`
	   to write data from within the `io()` method; this allows output 
	   written when in a pause state to be buffered and then printed  
	   later (when the pause state ends).
	"""
	
	# INIT
	def __init__(self, config=None, **k):
		"""Pass config and/or kwargs."""
		
		# basic status
		self.__active = False
		self.__running = False
		self.__threaded = False
		
		# remote socket control
		self.__csock = None
		self.__cport = None
		self.__lineq = None
		self.__jformat = trix.ncreate('fmt.JCompact')
		
		# each subclass of Output must track its own pause status
		self.__pausestate = self.paused()
		
		try:
			#
			# CONFIG
			#  - If this object is a Runner subclass that's already set a 
			#    self.config value, then kwargs have already been merged
			#    into `config`.
			#
			config = self.config
		except:
			#
			#  - If not, we'll need to create the config from args/kwargs.
			#    Creating a config dict, then - regardless of whether 
			#    `config` is from an existing self.config property - update
			#    it with `k` (directly below).
			#
			config = config or {}
		
		#
		# UPDATE CONFIG WITH `k`
		#  - Runner can't take a URL parameter unless it's part of a class
		#    that converts URL (or whatever other `config` type) to a dict
		#    before calling Runner's __init__. 
		#  - Therefore... don't catch this error; let it raise immediately
		#    so the developer will know there's something wrong here.
		#  - BTW: What the developer needs to do is make sure the config
		#         passed here from a base class is given as a dict.
		#
		config.update(k)
		
		# 
		# CONFIG - COPY
		#  - Runner should work as a stand-alone class, so....
		#  - Keep a copy in case this Runner object is created as itself
		#    (rather than as a super of some other class).
		#
		self.__config = config
		
		# 
		# ENCODING HELPER
		#  - Encoding for decoding bytes received over socket connections.
		# 
		Output.__init__(self, config)
		
		
		#
		# running and communication
		#
		self.__sleep = config.get('sleep', DEF_SLEEP)
		
		# Let kwargs set the "name" property; otherwise name is generated
		# on request of property `self.name`.
		if 'name' in config:
			self.__name = str(config['name'])
		
		#
		# If CPORT is defined in config, connect to calling process.
		#
		if "CPORT" in config:
			#
			# Set up for communication via socket connection.
			#
			self.__lineq = trix.ncreate('util.lineq.LineQueue')
			self.__cport = p = config["CPORT"]
			self.__csock = trix.ncreate('util.sock.sockcon.sockcon', p)
			try:
				self.__csock.writeline("%i" % trix.pid())
			except Exception as ex:
				trix.log("csock-write-pid", trix.pid(), type(ex), ex.args)
				self.__csock = None
				self.__lineq = None
	
	
	
	# ----------------------------------------------------------------
	# DEL
	# ----------------------------------------------------------------
	def __del__(self):
		"""Stop. Subclasses override to implement stopping actions."""
		try:
			try:
				self.stop()
			except Exception as ex:
				trix.log(
						"err-runner-delete", "stop-fail", ex=str(ex), 
						args=ex.args, xdata=xdata()
					)
			
			if self.__csock:
				try:
					self.__csock.shutdown(SHUT_RDWR)
				except Exception as ex:
					trix.log(
							"err-runner-csock", "shutdown-fail", ex=str(ex), 
							args=ex.args, xdata=xdata()
						)
			
			if self.active:
				self.close()
		
		except BaseException as ex:
			trix.log("err-delete-ex", "shutdown-fail", ex=str(ex), 
					args=ex.args, xdata=xdata()
				)
		
		finally:
			self.__csock = None
	
	
	# ----------------------------------------------------------------
	#
	# PROPERTIES
	#  - Runner is often one of a set of multiple base classes that may
	#    fail (and deconstruct) during init, so its properties need to
	#    be available even if Runner.__init__ has not yet been called.
	#  - This helps prevent raising of irrelevant Exceptions that might
	#    mask the true underlying error.
	#
	# ----------------------------------------------------------------
	
	@property
	def active(self):
		"""True if open() has been called; False after close()."""
		try:
			return self.__active
		except:
			self.__active = False
			return self.__active
	
	@property
	def running(self):
		"""True if running."""
		try:
			return self.__running
		except:
			self.__running = None
			return self.__running
	
	@property
	def threaded(self):
		"""True if running in a thead after call to self.start()."""
		try:
			return self.__threaded
		except:
			self.__threaded = None
			return self.__threaded
	
	@property
	def sleep(self):
		"""Sleep time per loop."""
		try:
			return self.__sleep
		except:
			self.__sleep = DEF_SLEEP
			return self.__sleep
	
	@sleep.setter
	def sleep(self, f):
		"""Set time to sleep after each pass through the run loop."""
		self.__sleep = f
	
	@property
	def name(self):
		"""
		Return the runner name, if one was provided to the constructor
		via kwarg "name". (Otherwise, a name will be generated using the
		pattern "<class_name>-<thread_ident>".)
		"""
		try:
			return self.__name
		except:
			self.__name = "Runner-%s" % str(self.ident)
			return self.__name
	
	@property
	def ident(self):
		"""Return thread-id."""
		return thread.get_ident()
	
	@property
	def config(self):
		"""The configuration dict - for reference."""
		try:
			return self.__config
		except:
			self.__config = {}
			return self.__config
	
	@property
	def csock(self):
		"""
		Used internally when opened with trix.process(), or any time a
		keyword argument "CSOCK" is given. 
		"""
		try:
			return self.__csock
		except:
			self.__csock = None
			return self.__csock
	
	
	
	# ---- orisc -----
	
	# ----------------------------------------------------------------
	#
	# OPEN
	#
	# ----------------------------------------------------------------
	def open(self):
		"""
		Called by run() if self.active is False.
		
		Override this method adding any code that needs to execute in
		order for the subclass to work. 
		
		Call `open` From Subclasses! If you override the `open` method,
		be sure to call `Runner.open()` exactly after all opening actions
		are complete so that the `Runner.active` flag will be set True.
		"""
		self.__active = True
	
	
	# ----------------------------------------------------------------
	#
	# RUN
	#
	# ----------------------------------------------------------------
	def run(self):
		"""
		Loop while self.running is True, calling 	`urgent()` and `io()`,
		and `cio()` when a control port is specified.
		"""
		
		# prepare for run by calling open()
		if not self.active:
			self.open()
		
		# mark object as running
		self.__running = True
		
		# Call self.cio() only in cases where event loop if a control 
		xio = [self.io]
		if self.csock:
			xio.append(self.cio)
		
		while self.__running:
			try:
				# call io method (and self.cio if applicable)
				for fn in xio:
					fn()
				
				# manage pause-state
				ps = self.paused()
				if self.__pausestate != ps:
					self.__pausestate = ps
					if ps:
						self.on_pause()
					else:
						self.flushbuffer()
						self.on_resume()
				
				# sleep a little, now that we're out of the lock
				time.sleep(self.sleep)
			
			except KeyboardInterrupt:
				pass
		
		# Once processing is finished, `close()` and `stop()`.
		if self.active:
			self.shutdown()
			self.__csock = None
		 
	
	# ----------------------------------------------------------------
	#
	# IO 
	#  - This io() method must be overridden to perform the 
	#    functionality for which the subclass is intended.
	#
	# ----------------------------------------------------------------
		
	def io(self):
		"""
		For a Runner object, this method does absolutely nothing. All
		subclasses must override this method to perform repeating tasks
		once for each pass through `io()`.
		
		IMPORTANT: Never use `print()` to print output from the `io` 
		           method. Always use the `write` or `writeline` methods.
		           Forthcoming features make this rule very important.
		"""
		pass
	
	
	# ----------------------------------------------------------------
	#
	# STOP
	#
	# ----------------------------------------------------------------
	def stop(self):
		"""Stop the run loop."""
		self.__running = False
		self.__threaded = False
	
	
	# ----------------------------------------------------------------
	#
	# CLOSE
	#
	# ----------------------------------------------------------------
	def close(self):
		"""
		This placeholder is called on object deletion. It may be called
		anytime manually, but you should probably call .stop() first if
		the object is running. Subclasses may call `close()` inside the
		`stop()`. 
		
		In any case, it's very important to call Runner.close() from
		subclasses so that the active flag will be set to false.
		"""
		self.__active = False
	
	
	
	# ---- handle CPORT socket queries -----
	
	# ----------------------------------------------------------------
	# CPORT-IO
	# ----------------------------------------------------------------
	def cio(self):
		"""
		This is called regularly, regardless of pause-state, when a
		remote socket controls cport.
		"""
		
		# read the control socket and feed data to the line queue
		c = self.csock.read()
		self.__lineq.feed(c)
		
		# read and handle lines from controlling process
		q = self.__lineq.readline()
		while q:
			# get query response
			r = self.query(q)
			
			# package and send reply
			if not r:
				r = dict(query=q, reply=None, error='unknown-query')
			
			# write the query back to the caller
			self.csock.writeline(self.__jformat(r))
			
			# read another line (returns None when done)
			q = self.__lineq.readline()
		
	
	# QUERY
	def query(self, q):
		"""
		Answer a query from a controlling process. Responses are always
		sent as JSON dict strings.
		
		Override this method in subclasses that can run in an external
		process, adding commands your class should respond to.
		"""
		if q:
			q = q.strip()
			if q == 'ping':
				return dict(query=q, reply='pong')
			elif q == 'status':
				return dict(query=q, reply=self.status())
			elif q == 'shutdown':
				# stop, returning the new status
				self.stop()
				r = dict(query=q, reply=self.status())
				return r
	
	
	# ---- callbacks -----
	
	def on_pause(self):
		pass
	
	def on_resume(self):
		pass
	
	
	# ---- utility -----
	
	# START
	def start(self):
		"""Start running in a new thread."""
		try:
			trix.start(self.run)
			self.__threaded = True
		except Exception as ex:
			msg = "err-runner-except;"
			trix.log(msg, str(ex), ex.args, type=type(self), xdata=xdata())
			self.stop()
			raise
	
	
	# STARTS - Start and return self
	def starts(self):
		"""Start running in a new thread; returns self."""
		self.start()
		return self
	
	
	# SHUTDOWN
	def shutdown(self):
		"""Stop and close."""
		with thread.allocate_lock():
			try:
				self.stop()
				self.close()
			except Exception as ex:
				msg = "Runner.shutdown error;"
				trix.log(msg, str(ex), ex.args, type=type(self))
				raise
	
	
	# STATUS
	def status(self):
		"""Return a status dict."""
		return dict(
			ek       = self.ek,
			active   = self.active,
			running  = self.running,
			threaded = self.threaded,
			sleep    = self.sleep,
			config   = self.config,
			cport    = self.__cport,
			
			paused   = self.paused()
		)
	
	
	# DISPLAY
	def display(self):
		"""Print status."""
		trix.display(self.status())
	
	
	
	#
	# EXPERIMENTAL
	#  - Try a console
	#
	def console(self):
		# REM: pause and resume are classmethods
		if self.paused():
			trix.ncreate("x.console.Console").console()
		else:
			try:
				self.pause()
				trix.ncreate("x.console.Console").console()
			finally:
				self.resume()

