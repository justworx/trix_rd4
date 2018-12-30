#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import os
from .. import *
from ..data.cursor import *

class Walker(Cursor):
	# Walk through directories.
	
	def __init__(self, top, **k):
		wk = trix.kcopy(k, "topdown followlinks")
		Cursor.__init__(self, os.walk(top, **wk), **k)
	
	# now we can fetch cursor results as filtered by `use`...
	
	# we also need convenience methods for commonly needed tasks
	
	
	
	"""
	@classmethod
	def files(cls, top, fn=None, **k):
		wk = trix.kpop("topdown followlinks")
		for w in self.walk(top, **wk):
			
	
	#
	# These need to be handled differently... maybe find should be a
	# generator... i dunno... something's not right here.
	# 
	#
	def find(self, fn, **k):
		# 
		# Find files by name.
		#
		# Pass a callable function that recieves the triplet from walk
		# and returns True for selected items.
		# 
		for x in iter(self):
			if fn(x):
				print (x[0])
	
	def search(self, fn, **k):
		#
		# Search files by content.
		#
	"""
	



"""
class Walker(object):
	# Walk through directories.
	
	def __init__(self, topdown=True, followlinks=False):
		self.__topdown = True
		self.__followlinks = followlinks
	
	def walk(self, top, filter=None):
		ii = iter(os.walk(top, self.__topdown, self.__followlinks))
		for x in ii:
			self.onstep(x)
	
	def onstep(self, x):
		d={
			'top' : x[0],
			'dir' : x[1],
			'files' : x[2]
		}
		trix.display(d)
	
	def onerror(self, *a, **k):
		pass
	
"""
