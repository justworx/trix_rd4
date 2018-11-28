#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import * # trix, mime, enchelp
from ..util.stream.reader import Reader
from ..util.stream.writer import Writer
from ..util.open import Opener



class File(FileBase):
	"""Access plain files.""" 
	
	# OPEN
	def open(self, mode, **k):
		"""
		Return a file pointer fitting `mode`, kwargs, and default encoding
		as provided to this object's constructor.
		"""
		if not mode:
			raise Exception('err-open-fail', xdata(reason='mode-required'))
		if 'b' in mode:
			return Opener.open(self.path, mode, **self.sansEncoding(k))
		else:
			k.setdefault('encoding', DEF_ENCODE)
			return Opener.open(self.path, mode, **self.applyEncoding(k))
	
	
	# READ
	def read(self, mode=None, **k):
		"""Read complete file contents (from start)."""
		ek = self.applyEncoding(k) # apply default encoding
		k['mode'] = mode or ('r' if ek else 'rb')
		with self.reader(**k) as r:
			return r.read()
	
	
	# WRITE
	def write(self, data, mode=None, **k):
		"""Write complete file contents."""
		ek = self.applyEncoding(k)
		k['mode'] = mode or ('w' if ek else 'wb')
		with self.writer(**k) as w:
			i = w.write(data)
			w.flush()
			return i
	
	
	# READER
	def reader(self, **k):
		"""Return a Reader object."""

		#
		# APPLY DEFAULT ENCODING (as given to File constructor)
		#  - encoding/errors in k, with self.ek applied as defaults
		#
		k = self.applyEncoding(k)
		
		#
		# MODE
		#  - If there's an encoding specification, let the default mode 
		#    for opening the stream be `self.rt`. Absent a specified 
		#    encoding, use as default mode `rb`.
		# 
		k.setdefault('mode', 'r' if k.get('encoding') else 'rb')
		
		#
		# GET STREAM
		#
		try:
			# if stream is given, send kwargs directly to constructor
			stream = k.pop('stream')
		except KeyError:
			# otherwise, a stream should be opened by this File object.
			stream = self.open(**k)
			
		return Reader(stream, **k)
	
	
	# WRITER
	def writer(self, **k):
		"""Return a Writer object."""
		
		k = self.applyEncoding(k) # i think it should be like this
		#k.update(self.ek)        # not sure why i had it like this
		
		k.setdefault('mode', "w" if self.ek else "wb")
		k.setdefault('encoding', DEF_ENCODE)
		try:
			# if stream is given, send kwargs directly to Writer()
			return Writer(k.pop('stream'), **k)
		except KeyError:
			# ...else get stream from self.open()
			return Writer(self.open(**k), **k)

