#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.sock.sockcon import *
from ..util.lineq import *


class Connect(sockcon):
	"""A simple connection class with config and socket properties."""
	
	DefWait = 3
	
	def __init__(self, config=None, **k):
		"""
		Pass a url parsable by util.urlinfo, or config dict and/or 
		kwargs suitable to the util.sock.sockcon class. 
		
		Use the `Connect.request()` method when you want to write data 
		to the server and wait for a response. This constructor will 
		honor the "wait" keyword argument as the sort of "pseudo timeout"
		when waiting for the response to a message sent to the server. 
		"""
		sockcon.__init__(self, config, **k)
		
		self.__wait = self.config.get('wait', self.DefWait)
		self.__lineq = LineQueue()
	
	
	def __call__(self, msg=None, wait=None):
		"""Send a request. (Alias for `request`."""
		return self.request(msg, wait)
	
	
	@property
	def wait(self):
		return self.__wait
	
	@wait.setter
	def wait(self, f):
		self.__wait = float(f)
	
	
	#
	# REQUEST
	#
	def request(self, msg=None, wait=None):
		"""
		Packages a request `msg` to the connected server.
		
		If self.wait is a positive float value, that number of seconds 
		is the time request will wait for a response before returning
		None.
		
		If a float value for the optional `wait` argument is given, that
		value will be used instad as the number of seconds to wait.
		
		If data is read before the wait time is up, the reading will
		continue until exhausted (even if the wait time is exceeded) and 
		the entire result returned.
		
		If argument `msg` is None, the same attempt is made to read more
		data that may have arrived after previous calls to `request` 
		ended.
		"""
		w = wait or self.wait
		t = time.time() + w
		r = []
		b = True
		x = None
		
		# determine whether to use `write` or `send`
		if self.encoding:
			fread = self.read
			fwrite = self.write
		else:
			fread = self.send
			fwrite = self.recv
		
		# send message `msg`
		if msg:
			fwrite(" -- " + msg)
			time.sleep(0.01)
		
		# loop waiting for received data until `wait` time ends
		while b or x:
			x = fread()
			if x:
				r.append(x)
				b = False
			elif time.time() > t:
				# REM: This doesn't stop the loop if `x` is not None
				b = False
			
			# wait 1/20th second
			if b or x:
				time.sleep(0.05)
		
		return ''.join(r)
	


