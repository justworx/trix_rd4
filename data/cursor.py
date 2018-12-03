#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .param import *


class Cursor(object):
	"""A cursor for any iterable object."""
	
	def __init__(self, data=None, **k):
		"""Pass any kind of `data` plus optional `use` callback kwarg."""
		
		# get optional param object
		self.__param = k.get('param', Param)
		
		# get the use method
		self.__use = k.get('use')
		
		# use must be callable
		if self.__use and (not callable(self.__use)):
			raise Exception('cursor-create-fail', 
				xdata(reason='callback-not-callable', callback=use)
			)
		
		# create the correct generator for the given data
		self.__gen = k.get('gen', self.generator(data, **k))
		
		# store the Fetch property object
		self.__fetcher = Fetch(self.__gen)
	
	def __call__(self, fn):
		"""Add a new cursor over the current one to manipulate results."""
		
		#
		# REM: Do not pass self.__gen as a keyword argument or it will
		#      use exactly that generator, which belongs to self, not
		#      to the new Cursor being created here. Passing it as gen=
		#      will just yeild exactly the results this (self) would.
		#      By passing it as the data, the generator will (or should)
		#      create a new generator that honors the new `use` lambda.
		#
		return Cursor(self.__gen, use=fn)
	
	
	def __iter__(self):
		return self.gen
	
	
	@property
	def gen(self):
		return self.__gen
	
	@property
	def fetch(self):
		"""Return the fetcher"""
		return self.__fetcher
	
	@property
	def param(self):
		"""Return the current (last-read) param object."""
		return self.__fetcher.param
	
	
	def values(self):
		"""
		Return a list of values (the value of each generated Param).
		This could be a list of lists, dict, string, or even complex 
		objects - it's the final result of all processing.
		"""
		return [p.v for p in self.__gen]
	
	
	def gentype(self, x=None, **k):
		"""
		Return a generator suitable to the type and/or attributes of the
		argument object `x`.
		"""
		
		# if it's already a generator, wrap it in a new generator so as to
		# allow for the stacking of `use` methods.
		if (type(x).__name__ == 'generator'):
			return self.gengen
		
		# text input (via file, url, or string) will probably be the most
		# common *FIRST* thing to be cursored over, then yielding a list
		# to parse; in such cases, though, the list is probably a list of
		# lists or dicts which will need to be "recursed", so it might be
		# best file or string io is lower in the list
		try:
			x.readline
			return self.genlines
		except AttributeError:
			# this object does not have .readline()
			pass
		
		# list, dict, and string will probably be the most common types
		# when recursing; unfortunately, they have to come in the wrong
		# order; Maybe I can find a way to improve speed here.
		try:
			x.keys
			x.__getitem__
			return self.genmap
		except AttributeError:
			pass
		
		# make sure a string isn't thrown in with list, tupel, etc...
		if isinstance(x, basestring):
			return self.genval
		
		# any sequence that doesn't have keys
		# REM: MUST come after dict
		try:
			x.__getitem__
			return self.genseq
		except AttributeError:
			pass
		
		try:
			if x == x.__iter__():
				return self.geniter
		except Exception:
			pass
		
		# if all else fails...
		return self.genval
	
	
	
	
	def generator(self, data=None, **k):
		"""
		The generator method returns the cursor module generator 
		best-suited to the type of data you pass it. 
		"""
		if 'gen' in k:
			return k['gen']
		
		gen = self.gentype(data, **k)
		return gen(data)
	
	
	def gengen(self, x):
		"""Yield from a generator."""
		param = self.__param()
		use = self.__use
		for p in x:
			if use:
				for i,v in enumerate(x):
					param.v = v
					param.i = i
					if use(param):
						yield param
			else:
				for i,v in enumerate(x):
					param.v = v
					param.i = i
					yield param
			
	
	def genval(self, x):
		"""Yield a single value."""
		p = self.__param
		p.v = x
		p.i = None
		if not self.__use:
			yield p
		elif self.__use(p):
			yield p
		
	
	def genseq(self, x):
		"""Yields each item for list (or list-like object) `x`."""
		param = self.__param()
		use = self.__use
		if use:
			for i,v in enumerate(x):
				param.v = v
				param.i = i
				if use(param):
					yield param
		else:
			for i,v in enumerate(x):
				param.v = v
				param.i = i
				yield param
			
		
	def genmap(self, x):
		"""Yields each key for dict (or dict-like object) `x`."""
		param = self.__param()
		use = self.__use
		if use:
			for i,v in enumerate(x):
				param.i = v
				param.v = x[v]
				if use(param):
					yield param
		else:
			for i,v in enumerate(x):
				param.i = v
				param.v = x[v]
				yield param
	
		
	def genlines(self, x):
		"""Yield lines for stream object `x`."""
		param = self.__param()
		use = self.__use
		i = 0
		if use:
			for line in x:
				param.v = line
				param.i = i
				i += 1
				if use(param):
					yield param
		else:
			for line in x:
				param.v = line
				param.i = i
				i += 1
				yield param
	
	
	def geniter(self, x):
		"""Yield the next item for iterator."""
		param = self.__param()
		use = self.__use
		i = 0
		if use:
			for v in x:
				param.v = v
				param.i = i
				i += 1
				if use(param):
					yield param
		else:
			for v in x:
				param.v = v
				param.i = i
				i += 1
				yield param



#
#
#  ---- FETCH -----
#
#
class Fetch(object):
	#
	# FETCH
	#  - An object of this class is set as a property in Cursor.
	#
	#  - It acts as the fetch method when called as a function...
	#    >>> cursor.fetch()         # returns next item value
	#
	#  - But it is an object...
	#    >>> cursor.fetch           # returns the fetch object
	#    >>> cursor.param.i         # returns current key/offset
	#    >>> cursor.param.v         # returns current value 
	#    >>> cursor.param.iv        # returns (i,v)
	#    >>> cursor.param.vi        # returns (v,i)
	#
	#  - For easy access...
	#    >>> cursor.param           # returns cursor.fetch.param
	#
	def __init__(self, gen):
		self.__gen = iter(gen)
		
		# set up the fetch method
		try:
			self.__fetch = self.__gen.__next__ # python 3
		except:
			self.__fetch = self.__gen.next     # python 2
		
		#
		# DO NOT DEFINE __PARAM UNTIL FIRST LINE IS READ!
		#  - only the self.__next or self.__call__ methods should set
		#    the value of self.__param
		#
		#self.__param = None; # do not uncomment!
		#
	
	# CALL
	def __call__(self):
		"""Return the next value."""
		return self.__next().v
	
	# NEXT
	def __next(self):
		"""Return next param object."""
		self.__param = self.__fetch()
		return self.__param
	
	@property
	def param (self):
		"""Return current param object (reading first, if necessary)."""
		return self.p
	
	@property
	def p (self):
		"""Return current param object (reading first, if necessary)."""
		try:
			return self.__param
		except AttributeError:
			return self.__next()
	
	@property
	def i (self):
		"""Return index or key of the current item."""
		return self.param.i
	
	@property
	def v (self):
		"""Return value of the current item."""
		return self.param.v
	
	@property
	def iv (self):
		"""Return index and value of the current item as a tuple."""
		return self.param.iv
	
	@property
	def vi (self):
		"""Return value and index of the current item as a tuple."""
		return self.param.vi



