#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

import signal
from .. import *


class Signals(object):
	"""
	Manage multiple signal objects.
	
	Signals consists purely of classmethods that handle Signal objects
	globally. It must be preconfigured in the main thread. Signal 
	handlers can not be set anywhere but the main thread. Setting a
	signal handler outside the main thread will result in failure and
	will probably disrupt all signal handling.
	
	INSTRUCTIONS FOR USE:
	 * Call classmethod `add` passing int `signal` and a function,
	   method, or other callable to be triggered when the specified
	   `signal` is detected.
	 * Use classmethod `rmv` to remove the signal when the target 
	   should	no longer receive notification of this signal.
	
	#
	# THIS CLASS MAY BE DEFINED *ONLY* IN THE MAIN THREAD!
	#
	Failure to use this class properly may result in the loss of any
	ability to respond to or manage signals during the process session.
	"""
	
	@classmethod
	def add(cls, signal, fn, **k):
		try:
			# Assume the whole thing's set up; this makes subsequent calls
			# respond faster.
			cls.__signals[signal].add(fn)
		except:
			# If there's an error, check that the __signals dict exists.
			try:
				cls.__signals
			except:
				cls.__signals = {}
			
			# Make sure the Signal object is defined in the __signals dict.
			if not signal in cls.__signals:
				cls.__signals[signal] = Signal(signal, **k)
			
			# Finally, add the signal callback.
			cls.__signals[signal].add(fn)
	
	@classmethod
	def rmv(cls, signal, fn):
		try:
			cls.__signals[signal].rmv(fn)
		except (AttributeError, KeyError):
			# Ignore AttributeError or KeyError, which would simply mean
			# that either `self.__signals` or `fn` does not exist... which
			# is the effect we're looking for anyway.
			pass
	
	#
	# TEMPORARY - FOR DEBUGGING
	#
	@classmethod
	def DEBUG_signals(cls):
		return cls.__signals




class Signal(object):
	"""
	Manages the handling of one signal.
	
	This class is intended to manage handling of one signal by passing
	notification of the signal on to zero or more separate functions,
	methods, or callables of any sort.
	
	If you want only specific objects to receive signal notification,
	pass an object-method to `Signal.add()`. If every object of a given
	class needs to handle the signal, pass a classmethod.
	
	Store any object methods so that they may be removed before the
	object's destruction.
	
	WARNING: THIS CLASS MUST OPERATE FROM THE MAIN THREAD!
	
	"""
	
	def __init__(self, signalnum, **k):
		"""
		Pass int `signalnum`. This value is only set on the first call to 
		this object's `__init__` method. It can't be reset by calling
		__init__ again. 
		
		The previous signal handler will be stored, then later restored 
		by this object's `__del__` method.
		
		Pass a keyword argument suppression=True if you want the default
		action to be suppressed when no handlers are present.
		
		Pass a keyword argument transparent=True if you want the signal
		to be handled by the `self.prior` handler after processing by the
		`Signal.handle` method. NOTE: This overrides the 'suppression'
		keyword argument; If "transparent" is True, signals are always
		handled by the default handler after other processing.
		"""
		
		self.__transparent = k.get("transparent", False)
		self.__suppression = k.get("suppression", False)
		
		# Only allow self.__signal and self.__prior be set here in the
		# first call to __init__.
		try:
			self.__signal
		except:
			self.__signal = signalnum
		
		try:
			self.__prior
		except:
			self.__prior = signal.signal(self.signal, self.handle) 
		
		try:
			self.__handlers
		except:
			self.__handlers = []
	
	
	#
	# DEL
	#
	def __del__(self):
		"""Reset to prior handler."""
		
		# if there was a previous handler, reset it
		if self.prior:
			self.__prior = None
		
		# delete this objects handlers
		try:
			del(self.__handlers)
		except:
			pass
	
	
	
	#
	# properties
	#
	@property
	def signal(self):
		"""Return the signal (int) this object reports on."""
		return self.__signal
	
	@property
	def prior(self):
		return self.__prior
	
	
	
	#
	# HANDLE - Handle a signal.
	#
	def handle(self, signal, stackframe):
		"""Call each signal-handler function."""
		
		if self.__handlers:
			#
			# Call each signal handler function. Store any handler that
			# fails (in rmvlist) and call its remove method.
			#
			try:
				rmvlist = []
				for handler in self.__handlers:
					try:
						handler(signal, stackframe)
					except BaseException as ex:
						# add failed handler to the remove list
						rmvlist.append(handler)
						raise type(ex)("err-signal-handler", trix.xdata(
								signal=signal, stackframe=stackframe, 
								result="signal-handler-removed"
							))
			except:
				# remove any handler that caused an exception
				for handler in rmvlist:
					self.__handlers.remove(handler)
				
				raise
				
				
		if self.__transparent:
			self.prior(signal, stackframe)
		elif not self.__handlers and not self.__suppression:
			self.prior(signal, stackframe)
	
	
	#
	# ADD
	#
	def add(self, fn):
		"""Set `fn` to be called on this Signal object's signal."""
		self.__handlers.append(fn)
			
	
	#
	# RMV
	#
	def rmv(self, fn):
		"""Remove a given `fn` from handlers."""
		self.__handlers.remove(fn)
	

