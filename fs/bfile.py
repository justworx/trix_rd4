#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .file import *

class BFile(File):
	"""
	Base for File-based wrappers whose streams work with bytes only.
	"""
	
	def __init__(self, path, **k):
		"""
		Pass optional defaults for mode, encoding, and errors as kwargs.
		These will be stored for use with the `reader()` and `writer()`, 
		but the file opening object will always open for reading bytes -
		that is, with mode 'rb' or 'wb'. Encoding defaults will be sent
		to `reader()` so that bytes from bytes-only files may be converted
		to unicode when specified.
		"""
		File.__init__(self, path, **k)
	
	
	# WRITER
	def writer(self, **k):
		"""Return a writer with given params, but opened in bytes mode."""
		self.applyEncoding(k)
		k.setdefault('mode', "w" if k.get('encoding') else "wb")
		return File.writer(self, stream=self.open("wb"), **k)
	
	
	# READ
	def read(self, mode=None, **k):
		"""Read complete file contents (from start)."""
		self.applyEncoding(k)
		k.setdefault('mode', mode or "r" if k.get('encoding') else "rb")
		return self.reader(**k).read()
	
	
	# READER
	def reader(self, **k):
		"""Return a reader with given params, but opened in bytes mode."""
		#
		# "Given params" means encoding passed to constructor, overridden
		# by any encoding passed to this method.
		#
		# It also means a 'mode' keyword specified by keyword args. To 
		# prevent errors, the default for BFile-based objects is 'rb'
		# unless there's an encoding - in which case it's 'r'.
		#
		# For BFile subclasses, the file stream itself is always opened in
		# binary mode. Any conversion to unicode happens in the reader (if
		# indicated by mode and encoding params).
		#
		
		# First, apply `self.ek` to `k` as defaults
		self.applyEncoding(k)
		
		# Then, calculate a default "mode" value
		k.setdefault("mode", "r" if k.get('encoding') else "rb")
		
		# Finally, return the reader that reads binary and converts it to
		# unicode if appropriate.
		return File.reader(self, stream=self.open("rb"), **k)
