#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .xqueue import Queue, Empty
from .enchelp import EncodingHelper, DEF_ENCODE, DEF_NEWL


class LineQueue(EncodingHelper):
	"""A queue containing lines of text."""
	
	def __init__(self, **k):
		"""Optional kwargs: q, a Queue object; newl, newline."""
		#
		# Lines implies text, so encoding should be passed if (and ONLY
		# if) text is being fed to the `feed` method.
		#
		EncodingHelper.__init__(self, **k)
		
		# a place to store incomplete lines
		self.__fragment = ''
		
		# make the queue (if one is not provided)
		self.__q = k.get('queue') or Queue()
		
		# set up the queue and newline-related values
		self.__newl = self.decode(k.get('newl', DEF_NEWL))
		"""
		#
		# This commented bit is being handled by the above line...
		# `self.__newl = self.decode(k.get('newl', '\r\n'))`
		#
		if self.ek:
			# if an encoding is given, bytes are being fed (written)
			try:
				self.__newl = self.__newl.decode(**self.ek)
			except AttributeError:
				# don't raise an exception when data is already unicode
				pass
		"""
		
		self.__nlen = len(self.__newl)
		if self.__nlen < 1:
			raise ValueError('err-newl-undefined')
	
	
	@property
	def q(self):
		return self.__q
	
	@property
	def newl(self):
		return self.__newl
	
	@property
	def nlen(self):
		return self.__nlen
	
	@property
	def fragment(self):
		return self.__fragment
	
	@property
	def lines(self):
		return iter(self.__lines())
	
	
	#
	# FEED
	#
	def feed(self, data, newl=False):
		"""Feed data to be queued."""
		
		if not data:
			return
		
		# convert bytes to unicode
		if self.ek:
			try:
				data = data.decode(**self.ek)
			except AttributeError:
				# don't raise an exception when data is already unicode
				pass
		
		# add newline
		if newl:
			data = data + self.newl
		
		# splitlines
		lines = data.splitlines(True)
		
		#
		# If there's a fragment, prepend it to the first item in `lines`.
		# This can only happen after the first feed has completed. It only
		# happens if the last line in the previous feed did NOT end with
		# whatever is specified in self.newl, eg..., CR, LF, CRLF, etc...
		#
		if self.fragment:
			lines[0] = self.fragment + lines[0]
			self.__fragment = '' # once it's prepended, discard the fragment
		
		ct = 0
		ln = len(lines)
		j = 1
		for line in lines:
			if line[-self.__nlen:] == self.newl:
				self.__q.put(line)
			else:
				self.__fragment = line
	
	
	# FEED-LINE
	def feedline(self, data):
		self.feed(data, True)
	
	
	
	#
	# READING
	#
	
	# READLINE
	def readline(self):
		"""Return the next queued line."""
		try:
			return self.__q.get_nowait()
		except Empty:
			return None
	
	# READ-LINES
	def readlines(self):
		return [line for line in self.lines]
	
	# READ
	def read(self):
		return ''.join([line for line in self.lines])
	
	
	def __lines(self):
		while True:
			try:
				yield self.q.get_nowait()
			except:
				raise StopIteration()

