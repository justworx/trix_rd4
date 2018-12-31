#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import os
from .. import *
from ..util.xiter import *
from ..data.cursor import *


class Walker(xiter):
	# Try it as an xiter...
	
	def __init__(self, top, **k):
		wk = trix.kcopy(k, "topdown followlinks")
		xiter.__init__(self, os.walk(top, **wk))

	def __next__(self):
		try:
			self.__data = xiter.__next__(self)
			return self
		except TypeError as ex:
			raise TypeError(*ex.args, xdata())
	
	@property
	def data(self):
		try:
			return self.__data
		except AttributeError:
			self.__data = xiter.__next__(self)
			return self.__data
	
	@property
	def path(self):
		return self.data[0]
	
	@property
	def pathlist(self):
		return self.data[0].split("/")
	
	@property
	def filelist(self):
		return self.data[2]
	
	@property
	def dirlist(self):
		return self.data[1]
	



"""
	
	def query(self, source, fn):
		r = []
		for item in source:
			x = fn(item)
			if x:
				r.append(x)
	

	
class walker_query(

	def filequery(self, action='select', **k):
		#
		#Perform actions on the current directory's files.
		#
		#Pass action from this list: ["select"]. Default is "select".
		#More actions may (probably) become available in the future.
		#
		#The 'select' action returns a list of files that match given
		#keyword arguments.
		#
		#Keyword arguments:
		# * stat : a list of constants from stats constrain the results
		#
		
		r = []
		for p in self.filelist:
			pp = path(self.path)(p)
			st = os.stat(pp)
			
"""


"""

class Walker(Cursor):
	# Walk through directories.
	
	def __init__(self, top, **k):
		wk = trix.kcopy(k, "topdown followlinks")
		Cursor.__init__(self, os.walk(top, **wk), **k)
	
	# now we can fetch cursor results as filtered by `use`...
	
	# we also need convenience methods for commonly needed tasks
	
	
	
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
