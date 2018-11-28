#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .xinspect import *


class Wrap(object):
	"""
	Wraps an object.
	
	Wrap is useful when you want to call an object by passing the name
	of its attributes as a string. Pass as text the name of a function, 
	method, or attribute, along with any args/kwargs where applicable.
	
	Public methods of the wrapped object are available to be called by
	passing the string name of a wrapped object's property, method, or
	attribute.
	
	>>> w = Wrap(Dir())
	>>> w('path')
	>>> w('cd', '..')
	>>> w('ls')
	
	
	NEW FEATURE - EXPERIMENTAL:
	
	Wrap's intended purpose is to faciliate calling of object methods
	and properties using strings - particularly for use by command line
	interfaces. However, as a convenience it implements - in addition
	to __init__ - __call__, __getattr__, __getitem__, and __setitem__. 
	Therefore, the wrapped object can in many cases be called using dot
	notation and list and dict objects may be used to a degree as well.
	
	>>> w = Wrap([1,2,3])
	>>> w.append(4)
	>>> w.o               # [1, 2, 3, 4]
	>>> w[0] = 9
	>>> w.o               # 
	>>> w[0]              # 9
	"""
	
	def __init__(self, o):
		"""Pass an object or module as the `o` argument."""
		
		# store object and inspector
		self.o = o
		self.i = Inspect(o)
		
		# store keys and attributes
		self.__keys = []
		self.__attrs = dir(self.o)
		for a in self.__attrs:
			if not ("__" in a):
				attr = getattr(self.o, a)
				self.__keys.append(a)
	
	def __repr__(self):
		"""Pass an object or module as the `o` argument."""
		Tself = type(self)
		return "<%s type=%s%s>" % (
				Tself.__name__, type(self.o).__name__,
				" (wrapper)" if Tself!=Wrap else ''
			)
	
	def __call__(self, key, *a, **k):
		"""
		Call any wrapped executable function, method, or property. For
		attributes, the value is returned (which exposes methods, too).
		
		>>> w = Wrap(trix.ncreate('fs.dir.Dir'))
		>>> w('ls')   # returns the result of the `Dir.ls()` method.
		>>> w('path') # returns the value of the `Dir.path` property.
		"""
		if key in self.i.methods:
			return self.i.methods[key](*a, **k)
		elif key in self.i.functions:
			return self.i.functions[key](*a, **k)
		elif key in self.i.properties:
			return self.i.properties[key].fget(self.o, *a)
		elif key in self.__keys:
			return getattr(self.o, key)
			return self.__attrs[self.__attrs.indexof(key)]
		else:
			raise KeyError(key)
	
	#
	# Additional experimental retrieval methods
	#
	def __getattr__(self, name):
		return getattr(self.o, name)
	
	def __getitem__(self, key):
		return self.o[key]
	
	def __setitem__(self, key, value):
		self.o[key] = value



