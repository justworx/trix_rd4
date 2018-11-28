#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .. import *


class Bag(object):
	"""A selection of values, sorted by name."""
	
	def __init__(self, T):
		"""Pass the type of object this bag holds."""
		try:
			self.__d = Bag.defaultdict(T)
		except:
			Bag.defaultdict = trix.value("collections.defaultdict")
			self.__d = Bag.defaultdict(T)
			
	
	def __getitem__(self, key):
		"""Get dict item."""
		return self.__d[key]
	
	def __setitem__(self, key, value):
		"""Directly set dict item."""
		self.__d[key] = value

	
	@property
	def dict(self):
		"""Return the current dict value."""
		return dict(self.__d)
	
	def put(self, key, value):
		"""Set or change a key/value pair."""
		self.__d[key] = value
	
	def get(self, key):
		"""
		Get value of key. Default may not be specified - it's always the
		empty value of the object's type.
		
		>>> b = Bag(int)
		>>> b.put("one", 1)
		>>> b.get("one") # 1
		>>> b.get("two") # 0
		"""
		return self.__d[key]
	
	def add(self, key, x):
		"""
		Add `x` to key value. If unset, set key's value to `x`.
		
		>>> b = Bag(int)
		>>> b.add("one", 1)
		>>> b.add("one", 1)
		>>> b.dict # {'one': 2}
		"""
		try:
			self.__d[key] += x
		except KeyError:
			self.__d[key] = x
	
	def append(self, key, x):
		"""
		Append x to bags of list-like types.
		
		>>> b = Bag(list)
		>>> b.append('foo', 1)
		>>> b.append('foo', 2)
		>>> b.dict # {'foo': [1, 2]}
		"""
		try:
			self.__d[key].append(x)
		except KeyError:
			self.__d[key] = [x]
		


