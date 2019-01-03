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
		"""Path (fs.Path) object for current directory."""
		return trix.path(self.data[0])
	
	@property
	def itempath(self):
		"""String path to current directory."""
		return self.data[0]
	
	@property
	def pathlist(self):
		"""List of path elements for current item."""
		return self.data[0].split("/")
	
	@property
	def dirlist(self):
		"""List of subdirectories in current directory."""
		return self.data[1]
	
	@property
	def filelist(self):
		"""List of file names in current directory."""
		return self.data[2]
	
	
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
		
		# prefetch first item; set item count to 0.
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
		"""The string path for the current file or directory."""
		return self.fspath.path
	
	@property
	def fspath(self):
		"""The fs.Path object wrapping this item."""
		return trix.path(self.w.path)(self.x)
	
	@property
	def dirpath(self):
		"""
		Return the full directory path string for the current item,
		either a full file path or full directory path, depending on
		the subclass.
		"""
		return self.__dirpath
	
	@property
	def filelist(self):
		"""Return a list of all files in the current directory."""
		return self.walker.filelist





class file_selector(walker_selector):
	
	def __init__(self, walker):
		walker_selector.__init__(self, walker, walker.filelist)
	
	
	#
	# This is explorator but... maybe like this: 
	#
	def query(self, selection, action):
		"""
		Pass a selection function and an action function. 
		
		This method loops through all files in self.filelist. Any files
		selected by the selection function (if it returns True) will be
		altered by the action function. Both `selection` and `action`
		receive `self` (this object) as their only argument.
		"""
		if selection(self):
			action(self)
	
	#
	# if this ends up working, it will probably be moved to the
	# walker_selector class - it's simple enough to be shared by
	# both file_selector and dir_selector (coming soon).
	#


