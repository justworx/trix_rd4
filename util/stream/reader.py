#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *
#from ...view import * # trix, Stream, enchelp


class Reader(Stream):
	"""Reader of streams."""
	
	def __init__(self, stream, **k):
		"""
		Pass the required `stream` object. If the optional `encoding`
		and/or mode kwargs are passed, keyword argument is specified, they
		will be used to determine encoding of values returned by reading
		methods and the `lines` property.
		
		When kwarg "mode" contains 'b' and an encoding is provided, the 
		given stream is (by default) buffered. This is so that readlines
		will work correctly in all cases. Pass kwarg buffer=False to 
		prevent this behavior. Pass buffer=True to force this behavior 
		even with non-binary streams. (This can be useful if you need 
		more extensive seeking operations than the default provided by 
		most file streams.) 
		"""
		
		# init with stream
		Stream.__init__(self, stream, **k)
		
		# Set this object's `next` method so it will be available from
		# earlier python versions.
		#self.next = self.__next__ # p2/p3
	
	def __iter__(self):
		"""Line iterator."""
		return self.lines
	
	def __next__(self):
		"""Read and return the next line."""
		return next(self.lines)
	
	
	@property
	def lines(self):
		"""Generator: Yields one line at a time."""
		x = self.readline()
		while x:
			yield x
			x = self.readline()
		raise StopIteration()
	

	@property
	def bytes(self):
		"""Generator: Yields one byte at a time."""
		if not "b" in self.mode:
			raise TypeError("err-bytes-fail", xdata(mode=self.mode,
					suggest=['open-mode-b', 'provide-correct-encoding'],
					reason="byte-mode-required"
				))
		b = self.read(1)
		while b:
			yield b
			b = self.read(1)
		raise StopIteration()


	@property
	def chars(self):
		"""Generator: Yields one unicode character at a time."""
		if 'b' in self.mode:
			raise TypeError("err-chars-fail", xdata(mode=self.mode,
					suggest=['remove-mode-b', 'provide-correct-encoding'],
					reason="text-mode-required"
				))
		x = self.read(1)
		while x:
			yield x
			x = self.read(1)
		raise StopIteration()


	#
	# READING PROPERTIES
	#  -
	#
	@property
	def read(self):
		"""Return all content from current position."""
		try:
			return self.__read
		except AttributeError:
			return self.__readinit
	
	@property
	def readline(self):
		"""Return content from current position to the next endline."""
		try:
			return self.__readline
		except AttributeError:
			return self.__readlineinit
	
	
	#
	# READING INITIALIZERS
	#
	def __readinit(self, *a):
		return self.__readinits(self.stream.read(*a))
	
	def __readlineinit(self, *a):
		return self.__readinits(self.stream.readline(*a))
	
	def __readinits(self, v, *a):
		"""Set the read() and readline() methods."""
		
		# MODE B - converts unicode to bytes - returns (B)ytes.
		if self.mode and ('b' in self.mode):
			try:
				# presume the value read `v` is unicode and try to encode it. 
				if isinstance(v, unicode):
					vv = v.encode(**self.ek) if self.ek else v.encode()
					
					# Python2 can throw you by encoding a string of bytes.
					# Don't let that stand.
					if isinstance(vv, unicode):
						raise AttributeError("Attempt to encode bytes.")
					
					# If all's well, we received unicode and will return bytes.
					# Set self.__readline readlineb(), and then return `v`.
					self.__read = readb(self)
					self.__readline = readlineb(self)
					return vv
			
			except AttributeError:
				# if there's an exception from the code above, that means the
				# stream is already producing bytes, so just ignore the error,
				# set readline to self.stream.readline, and return the value,
				# `v` that was read above.
				pass
		
		
		# MODE *NOT* B; 
		elif self.mode:
			try:
				# presume the value read `v` is bytes and try to decode it. 
				if isinstance(v, bytes):
					vv = v.decode(**self.ek) if self.ek else v.decode()
					
					# Python2 can throw you by decoding a string of unicode.
					# Don't let that stand.
					if isinstance(vv, bytes):
						raise AttributeError("Attempt to decode unicode.")
					
					# If all's well, we received bytes and will return unicode.
					# Set self.__readline to readlineu() and return `v`.
					self.__read = readu(self)
					self.__readline = readlineu(self)
					return vv
				
			except AttributeError:
				# If there's an exception from the code above, that means the
				# stream is already producing unicode; just ignore the error,
				# set readline to self.stream.readlineu, and return the value,
				# `v` that was read above.
				pass
		
		
		# Otherwise, read from the stream directly.
		self.__read = self.stream.read
		self.__readline = self.stream.readline
		return v




#
# READERS
#
class xreader(object):
	def __init__(self, x):
		self.x = x
		self.ek = x.ek
		self.mode = x.mode
		self.stream = x.stream

class readb(xreader):
	def __call__(self, *a):
		"""Read unicode from stream; encode and return it as bytes."""
		return self.stream.read(*a).encode(**self.ek)

class readu(xreader):
	def __call__(self, *a):
		"""Read bytes from stream; encode and return them as unicode."""
		return self.stream.read(*a).decode(**self.ek)
	
class readlineb(xreader):
	def __call__(self, *a):
		"""Read unicode from stream; encode and return it as bytes."""
		return self.stream.readline(*a).encode(**self.ek)

class readlineu(xreader):
	def __call__(self, *a):
		"""Read bytes from stream; encode and return them as unicode."""
		return self.stream.readline(*a).decode(**self.ek)
