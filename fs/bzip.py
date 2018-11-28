#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .bfile import *
import bz2


class Bzip(BFile):
	"""Handle bz2 files."""
	
	# OPEN
	def open(self, mode=None, **k):
		"""
		Pass `mode` 'rb' or 'wb', and optional compression level (1-9)
		defaults to 9. Optional encoding kwargs are used by the reader() 
		and writer() methods.
		"""
		ok = trix.kcopy(k, "compresslevel")
		return bz2.BZ2File(self.path, mode, **ok)
	
	# TOUCH
	def touch(self, times=None):
		"""Make sure file exists. If `times` is set, touch."""
		if not self.exists():
			with bz2.BZ2File(self.path, 'w'):
				pass
		if times:
			with bz2.BZ2File(self.path, 'a'):
				os.utime(self.path, times)
