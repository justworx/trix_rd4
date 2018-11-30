#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


import signal


#
# SIGNALS - Manage all Signal objects.
#
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
	def add(cls, signal, fn):
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
				cls.__signals[signal] = Signal(signal)
			
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
		
		Pass a keyword argument suppress=True if you want the default
		action to be suppressed when no handlers are present.
		"""
		
		self.__suppression = k.get("suppress", False)
		
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
			dbg = signal.signal(self.signal, self.prior)
			self.__prior = None
		
		try:
			# delete this objects handlers
			del(self.__handlers)
		except:
			pass
	
	
	
	@property
	def signal(self):
		"""Return the signal (int) this object reports on."""
		return self.__signal
	
	@property
	def prior(self):
		return self.__prior
	
	
	
	#
	# DEL
	#
	def handle(self, signal, stackframe):
		"""Call each signal-handler function."""
		
		if self.__handlers:
			#
			# Call each signal handler function. Store any handler that
			# fails, and call its remove method.
			#
			rmvlist = []
			for handler in self.__handlers:
				try:
					handler(signal, stackframe)
				except:
					#
					# DEBUGGING
					#
					trix.log(["DEBUG HANDLE:", xdata()])
					
					# add failed handler to the remove list
					rmvlist.append(handler)
			
			# remove any handler that caused an exception
			for handler in rmvlist:
				self.__handlers.remove(handler)
		
		if not self.__handlers and not self.__suppression:
			self.prior()
	
	
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
	

