#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ..fmt import *  #trix, time
import os


FMT_TIME = "%Y-%m-%d %H:%M:%S"
DEF_NAME = "./loglet"


class Loglet(object):
	"""Debugging Logger."""
	
	def __init__(self, path=DEF_NAME, **k):
		"""Pass the path to an output file. Default: './loglet'"""
		tag = trix.kpop(k, 'tag')
		path = "%s.%s" % (path, tag.get('tag', str(os.getpid())))
		self.logf = open(path, 'a', **k)
		self.logf.write('\n\n\n#\n# %s\n#\n' % time.strftime(FMT_TIME))
		self.logf.flush()
		
	
	def __del__(self):
		"""Closes loglet."""
		self.logf.flush()
		self.logf.close()
	
	def __call__(self, *a, **k):
		tm = time.strftime(FMT_TIME)
		entry = list(a)
		if k:
			entry.append(k)
		js = self.jout(entry)
		self.logf.write('\n"%s %f %i" = %s\n' % (
				tm, time.time(), trix.pid(), js
			))
		self.logf.flush()
	
	def jout(self, d):
		return JDisplay().format(d)
	
	
	def flush(self):
		"""Debugging. So I can flush from the interpreter."""
		if self.logf:
			self.logf.flush()
	