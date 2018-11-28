
#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import * # trix, Stream


class Buffer(Stream):
	"""A buffer. Write content in, then read it back out."""

	MAXSIZE = 2**16
	KWARGS = "suffix prefix dir".split()
	
	#
	# Pass an encoding if you want to write bytes. Otherwise, you'll 
	# need to send unicode data to `write()`.
	#
	def __init__(self, initialContent=None, **k):
		"""
		Pass optional `initialContent` argument as string or bytes, and
		optional keyword aruments:
		 - mode:     Read 'rb' bytes or 'r' unicode;
		 - encoding: The encoding used to convert to desired 'mode';
		 - errors:   The 'errors' value for encoding/decoding methods;
		 - max_size: The maximum size of buffer before tempfile is rolled
		             over to a file. (Only works on python 2.6+; otherwise
		             Buffer is always associated with a tempfile.) 
		"""
		self.__maxsize = k.get('max_size', self.MAXSIZE)
				
		# create the tempfile/buffer
		tk = trix.kpop(k, self.KWARGS)
		try:
			# py2.6+
			k['max_size'] = self.__maxsize
			self.__f = trix.create('tempfile.SpooledTemporaryFile', **tk)
		except:
			# py2.3+ has no SpooledTemporaryFile
			self.__f = trix.create('tempfile.NamedTemporaryFile', **tk)
		
		# call the superclass constructor
		Stream.__init__(self, self.__f, **k)
		self.__defmode = self.mode or 'r' if self.ek else 'rb'
		
		# set initial content
		if initialContent:
			self.write(initialContent)
			self.seek(0)
	
	
	def __del__(self):
		# try to empty the temp file, if it exists
		self.seek(0)
		self.__f.truncate()
		self.__f.flush()
	
	
	def __len__(self):
		pos = self.__f.tell()
		try:
			self.__f.seek(0,2)
			return self.__f.tell()
		finally:
			self.__f.seek(pos)
	
	
	@property
	def maxsize(self):
		"""The size at which the buffer rolls over to a file. (Py2.6+)"""
		return self.__maxsize
	
	@property
	def defmode(self):
		"""Default read mode ('r' or 'rb')."""
		return self.__defmode
	
	def truncate(self):
		"""Truncate the buffer at the current position."""
		self.__f.truncate()
	
	def flush(self):
		"""This method exists only to prevent errors when its called."""
		pass
	
	def close(self):
		"""Close the buffer stream."""
		if self.__f:
			self.__f = None
	
	# WRITE
	def write(self, data, **k):
		"""Write full content."""
		try:
			self.stream.seek(0)
			return self.writer(**k).write(data)
		finally:
			self.stream.seek(0)
	
	# READ
	def read(self, **k):
		"""Read full content."""
		try:
			self.stream.seek(0)
			return self.reader(**k).read()
		finally:
			self.stream.seek(0)
	
	# WRITER
	def writer(self, **k):
		"""Return a buffer Writer (at current position)."""
		self.applyEncoding(k)
		k.setdefault('mode', self.mode or self.__defmode)
		k.setdefault('keepopen', True)
		return trix.ncreate('util.stream.writer.Writer', self.__f, **k)
	
	# READER
	def reader(self, **k):
		"""Return a buffer Reader (at current position)."""
		self.applyEncoding(k)
		k.setdefault('mode', self.mode or self.__defmode)
		k.setdefault('keepopen', True)
		return trix.ncreate('util.stream.reader.Reader', self.__f, **k)
