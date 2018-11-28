#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *

class Stringer(object):
	"""
	Creates a list of simple values to be recast as strings.
	"""
	
	def __init__(self, encoding=None):
		"""Pass encoding for result strings. Default: DEF_ENCODE"""
		self.items = []
		self.encoding = encoding or DEF_ENCODE
	
	
	def __len__(self):
		return len(self.items)
	
	
	def add(self, *args):
		"""
		Pass *args of any type to be appended to the `self.items` list. 
		This may be called more than once.
		"""
		for a in args:
			self.items.append(a)
	
	
	def strings(self):
		"""
		Returns a list of `self.items`, each cast as a string.
		"""
		r = []
		for item in self.items:
			if isinstance(item, str):
				r.append(item)
			else:
				try:
					r.append(item.decode(self.encoding))
				except AttributeError:
					r.append(str(item))
		
		return tuple(r)


