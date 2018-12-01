#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .xthread import *
from .enchelp import * # trix
from .stream.buffer import *


DEF_SLEEP = 0.1


class Runner(EncodingHelper):
	"""
	Manage a (possibly threaded) event loop, start, and stop. Override
	the `io` method, defining actions that must be taken each pass 
	through the loop.
	"""
	
	# ---- SIGNAL HANDLING -----
	__interrupted = 0
	
	@classmethod
	def on_signal(cls, signum, stackframe):
		"""
		The SIGINT signal	toggles the "pause" state of all output. All
		Runner objects buffer output while in this pause-state, and write
		the buffered content when the pause-state is turned off.  
		"""
		if signum == 2:
			cls.__interrupted += 1
			cls.__paused = bool(cls.__interrupted % 2)
	
	
	# ---- PAUSE HANDLING -----
	__paused = False
	
	@classmethod
	def paused(cls):
		return cls.__paused
	
	
	
	# ----------------------------------------------------------------
	#
	# OBJECT METHODS
	#
	# ----------------------------------------------------------------
	
	# INIT
	def __init__(self, config=None, **k):
		"""Pass config and/or kwargs."""
		
		self.__active = False
		self.__running = False
		self.__threaded = False
		self.__interrupt = 0
		
		# get the current paused state
		self.__pausestate = self.paused()
		
		self.__csock = None
		self.__cport = None
		self.__lineq = None
		self.__jformat = trix.ncreate('fmt.JCompact')
		
		
		try:
			#
			# CONFIG
			#  - If this object is part of a superclass that's already set 
			#    a self.config value, then `config` and `k` are already part
			#    or all of it.
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
		EncodingHelper.__init__(self, config)
		
		
		#
		# running and communication
		#
		self.__newl   = config.get('newl', '\r\n')
		self.__output = out = config.get('output', sys.stdout)
		self.__sleep  = config.get('sleep', DEF_SLEEP)
		
		#
		# Choose the correct writer for the pause-status; if paused,
		# self.writer is a Buffer; otherwise, it's sys.stdout by defualt
		# (but may be specified by kwarg 'output').
		#
		self.__writer = Buffer(*self.ek) if self.paused() else out
		
		
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
				
	
	
	# DEL
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
	
	
	#
	# PROPERTIES
	#  - Runner is often one of a set of multiple base classes that may
	#    fail (and deconstruct) during init, so its properties need to
	#    be available even if Runner.__init__ has not yet been called.
	#  - This helps prevent raising of irrelevant Exceptions that might
	#    mask the true underlying error.
	#
	
	@property
	def active(self):
		"""True if open() has been called; False after close()."""
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
	def pausestate(self):
		"""Return the current pause state; True or False."""
		return self.__pausestate
	
	@property
	def name(self):
		"""Return the thread name."""
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
	
	@property
	def writer(self):
		"""Current writer; Eg., stdout or Buffer..."""
		return self.__writer
			
	
	
	# ---- orisc -----
	
	#
	# OPEN
	#
	def open(self):
		"""
		Called by run() if self.active is False.
		
		Override this method adding any code that needs to execute in
		order for the subclass to work. Call `Runner.open()`!)
		"""
		self.__active = True
	
	
	#
	# RUN
	#
	def run(self):
		"""
		Loop while self.running is True, calling 	`urgent()` and `io()`,
		and `cio()` when a control port is specified.
		
		The `io` method is not called when Runner.pause() returns True.
		"""
		
		# prepare for run by calling open()
		if not self.active:
			self.open()
		
		# mark object as running
		self.__running = True
		
		# Call self.cio() only in cases where event loop if a control 
		# socket has been successfully created...
		if self.csock:
			while self.__running:
				try:
					self.urgent()
					if not self.paused():
						self.io()
					self.cio()
					time.sleep(self.sleep)
				except KeyboardInterrupt:
					pass
		
		# ...otherwise call only `urgent()` and `io()`.
		else:
			while self.__running:
				try:
					self.urgent()
					if not self.paused():
						self.io()
					time.sleep(self.sleep)
				except KeyboardInterrupt:
					pass
		
		# Once processing is finished, `close()` and `stop()`.
		if self.active:
			self.shutdown()
	
	
	#
	# IO
	#
	def __io(self):
		#
		# check for change in pause state
		#
		if self.__pausestate != self.paused():
			self.__pausestate = self.paused()
			
			# while paused, output must be written to a buffer.
			if self.__pausestate:
				self.__writer = Buffer(**self.ek).writer()
				self.on_pause()
			
			else:
				# store the buffer for a sec...
				bfr = self.__writer
				
				# switch back to the real writer
				self.__writer = self.__write
				
				# write whatever was stored by the buffer
				self.write(bfr.read()) 
				self.on_resume()
		
		# call io()
		self.io()
		
		# if cport exists...
		
	
	
	#
	# IO 
	#  - The real io() method must be overridden to perform the 
	#    functionality for which the subclass is intended.
	#
	def io(self):
		"""Override this method to perform repeating tasks."""
		pass
	
	
	#
	# STOP
	#
	def stop(self):
		"""Stop the run loop."""
		self.__running = False
		self.__threaded = False
	
	
	#
	# CLOSE
	#
	def close(self):
		"""
		This placeholder is called on object deletion. It may be called
		anytime manually, but you should probably call .stop() first if
		the object is running. Some classes may call .close() in .stop().
		"""
		self.__active = False
	
	
	
	# ---- handle urgent actions -----
	
	def urgent(self):
		"""
		Override this method to handle urgent actions, such as continuing
		background processing or responding to connection-related input.
		
		The one thing that must not happen inside this method is output
		to the terminal. You must be sure that NOTHING is printed inside
		this method, or the effect of a pause state will be ruined.
		
		IMPORTANT:
		If you override the urgent method, you must call this inherrited
		method so that it can call the appropriate `on_pause()` or
		`on_resume()` method.
		"""
		if self.__pausestate != self.paused():
			self.__pausestate = self.paused()
			if self.__pausestate:
				# while paused, output must be written to a buffer.
				self.__writer = Buffer(**self.ek).writer()
				self.on_pause()
			else:
				# store the buffer for a sec...
				bfr = self.__writer
				
				# switch back to the real writer
				self.__writer = self.__write
				
				# write whatever was stored by the buffer
				self.write(bfr.read()) 
				self.on_resume()
	
	
	def on_pause(self):
		pass
	
	
	def on_resume(self):
		pass
	
	
	def write(self, text):
		self.__writer(text)
	
	
	
	# ---- handle CPORT socket queries -----
	
	# CPORT-IO
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
			writer   = self.writer,
			paused   = self.paused(),
			sleep    = self.sleep,
			config   = self.config,
			cport    = self.__cport
		)
	
	
	# DISPLAY
	def display(self):
		"""Print status."""
		trix.display(self.status())
	

