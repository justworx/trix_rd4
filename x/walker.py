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
	
	def __init__(self, top='.', **k):
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
		"""Path (fs.Path) object for current directory."""
		return trix.path(self.data[0])
	
	@property
	def itempath(self):
		"""String path to current directory."""
		return self.path(self.data[0]).path
	
	@property
	def pathlist(self):
		"""List of path elements for current item."""
		return self.itempath.split("/")[1:]
	
	@property
	def dirlist(self):
		"""List of subdirectories in current directory."""
		return self.data[1]
	
	@property
	def filelist(self):
		"""List of file names in current directory."""
		return self.data[2]
	
	
	@property
	def dirs(self):
		"""Directory selector for current path."""
		return dir_selector(self)
	
	@property
	def files(self):
		"""File selector for current path."""
		return file_selector(self)
	




class walker_selector(xiter):
	"""
	This class would be the base for file_selector and dir_selector
	subclasses, each of which would provide methods/properties that
	return the appropriate file- or directory-related features.
	"""
	def __init__(self, walker, itemlist):
		xiter.__init__(self, itemlist)
		self.w = walker
		self.x = None
		self.i = -1
		
		# prefetch first item; sets item count to 0.
		self.next()
	
	
	def __next__(self):
		self.x = xiter.__next__(self)
		self.i += 1
		return self
	
	
	@property
	def walker(self):
		"""The Walker object that generated this path/data."""
		return self.w
	
	@property
	def path(self):
		"""The fs.Path object wrapping this item."""
		return self.w.path(self.x)
	
	@property
	def name(self):
		"""The string path for the current file or directory."""
		return self.path.name
	
	@property
	def itempath(self):
		"""The string path for the current file or directory."""
		return self.path.path
	
	@property
	def filelist(self):
		"""Return a list of all files in the current directory."""
		return self.walker.filelist
	
	
	
	#
	# This is exploratory but, maybe *something* like this. Probably
	# the arguments will change - likely to kwargs, something like the
	# way data.udata.charinfo is done.
	#
	# I suspect I'll be playing with this for a long time before it's
	# conclusion, which very well may be the deletion of this file from
	# the project.
	#
	def query(self, selection=None, action=None):
		"""
		Pass a selection function and an action function. 
		
		This method loops through all files in self.filelist. Any files
		selected by the selection function (if it returns True) will be
		altered by the action function. Both `selection` and `action`
		receive `self` (this object) as their only argument.
		"""
		if not selection:
			selection = lambda x: True
		
		try:
			r = []
			while True:
				if selection(self):
					r.append(self.path)
					if action:
						action(self)
				self.next()
		except StopIteration:
			return r
	




class dir_selector(walker_selector):
	
	def __init__(self, walker):
		"""Call walker_selector init, passing the file list."""
		walker_selector.__init__(self, walker, walker.dirlist)
	




class file_selector(walker_selector):
	
	def __init__(self, walker):
		"""Call walker_selector init, passing the file list."""
		walker_selector.__init__(self, walker, walker.filelist)
	
	@property
	def stat(self):
		return os.stat(self.itempath)
	


