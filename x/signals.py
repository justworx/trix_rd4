#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

import signal


class Signal(object):
	"""
	Manages one signal's handling.
	
	This class is intended to manage handling of one signal by passing
	the signal on to zero or more objects that have been added to the
	list of recpients. 
	
	WARNING: THIS CLASS MUST OPERATE FROM THE MAIN THREAD!
	
	"""
	
	def __init__(self, signal):
		"""
		Pass int `signal`. This value is only set on the first call to 
		this object's `__init__` method. The previous signal handler will 
		be stored, then later restored by this object's `__del__` method.
		"""
		
		# Only allow self.__signal and self.__prior be set here in the
		# first call to __init__.
		try:
			self.__signal
		except:
			self.__signal = signal
		
		try:
			self.__prior
		except:
			self.__prior = signal.signal(signal, self.handle) 
		
		#
		# Allow for multiple handlers to receive notification of any 
		# given signal. To handle signals by class, pass a classmethod
		# as the target. Otherwise, pass the individual target method
		# that should receive a call when this signal is detected.
		# 
		self.__handlers = []
	
	
	def __del__(self):
		"""Reset to prior handler."""
		if self.__prior:
			signal.signal(self.__handle, self.__prior)
			self.__prior = None
	
	
	def __handle(self, signal, stackframe):
		"""Call each target function."""
		for i in range(0,len(self.__handlers)):
			try:
				self.__handlers[i](signal, stackframe)
			except:
				trix.display(xdata())
				remove(self.__handlers[i])
	
	
	@property
	def signal(self):
		"""Return the signal (int) this object reports on."""
		return self.__signal
			
	
	
	def add(self, fn):
		"""Set `fn` to be called on this Signal object's signal."""
		self.__handlers[ident] = fn
	
	
	def rmv(self, fn):
		"""Remove a given `fn` from handlers."""
		del(self.__handlers[fn])
	

