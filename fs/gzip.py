#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .bfile import *


class Gzip(BFile):
	"""Gzip file support."""
	
	# GZ OPEN
	def open(self, mode=None, **k):
		"""Return a gzip file pointer."""
		ok = trix.kcopy(k, "compresslevel")
		return trix.create("gzip.GzipFile", self.path, mode, **ok)
	
	# TOUCH
	def touch(self, times=None):
		"""Make sure file exists. If `times` is set, touch."""
		if not self.exists():
			with self.open("a") as fp:
				fp.write(b'')
				fp.flush()
				fp.close()
		
		# apply timestamp
		if times:
			BFile.touch(self, times)
