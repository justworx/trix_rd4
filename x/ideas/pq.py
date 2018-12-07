#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

import fnmatch

from trix.data.cursor import *
from trix.util.wrap import *

class pq(Wrap):
	"""
	UNDER CONSTRUCTION! EXPERIMENTAL!
	
	Pass a list or dict object. The given object will be wrapped by a
	util Wrap object, so the pq object should behave pretty much like
	the type passed to it, except it carries the operation forward 
	through a chain of calls.
	
	>>> from trix.x.pq import *
	>>> q = pq([1,2,3,4,5])
	
	# use wrapped list functions to affect the object
	>>> q.append(9)
	
	# use the `o` property to access the object directly
	>>> q.o # [1, 2, 3, 4, 5, 9]
	
	"""
		
	def __init__(self, o):
		"""Pass object `o` to the constructor.""" 
		Wrap.__init__(self, o)
	
	def __call__(self, fn, *a, **k):
		"""
		Return a new pq object containing the result of the given lambda,
		function, or other executable object.
		
		>>> q = pq([1,2,3])
		>>> qr = q(reversed)(list).o
		>>> qr
		[3, 2, 1]
		"""
		return pq(fn(self.o, *a, **k))
	
	
	
	
	# --- manipulation ---
	
	def each(self, fn, *a, **k):
		"""
		Passes a data Param to executable `fn` for each item.
		
		>>> def test(p):
		...   print(p.i, p.v) # print index, value
		... 
		>>> q = pq([1,2,3])
		>>> q.each(test)
		0 1
		1 2
		2 3
		"""
		c = Cursor(self.o)
		try:
			while True:
				c.fetch()
				fn(c.fetch.param, *a, **k)
		except StopIteration:
			pass
		return self
	
	
	def select(self, fn, *a, **k):
		"""
		Passes a data Param to executable `fn` for each item. Stores a
		list of results and returns that list wrapped as a pq object.
		
		# find all Runner methods
		from trix.x.ideas.pq import *
		from trix.x.runner import *
		from trix.util.wrap import *
		
		r = Runner()
		w = Wrap(r)
		
		mm = list(w.i.methods.keys())
		mq = pq(mm).select(lambda p: p.v and p.v[0] != '_')
		trix.display(mq(sorted), f='Table', width=7)
		"""
		c = Cursor(self.o, use=fn)
		try:
			r = []
			while True:
				r.append(c.fetch())
		except StopIteration:
			pass
		return pq(r)
	
	
	def update(self, fn, *a, **k):
		"""
		Pass executable object `fn`, which receives a Param object and 
		any args/kwargs passed to this method. The executable must alter
		the received Param (if necessary) and return it.
		>>> from trix.x.pq import *
		>>> q = pq([1,2,3,4,5])
		>>> q.update(lambda p: p.set(p.v*10))
		>>> q.o
		[10, 20, 30, 40, 50]
		"""
		c = Cursor(self.o)
		try:
			while True:
				p = None
				c.fetch()
				p = fn(c.fetch.param, *a, **k)
				self.o[p.i] = p.v
		except StopIteration:
			pass
		except Exception as ex:
			raise type(ex)(xdata(p=p.iv if p else None, a=a, k=k))


#
# UNDER CONSTRUCTION
#  - The following code is NOT in use - it's just an idea I'm keeping
#    here until i decide whether to pursue it (and, if so, how to
#    proceed with it).
#
class PQ_Select(object):
	"""Helper class for pq"""
	
	def __init__(self, pq, *a, **k):
		"""Pass the `pq` object."""
		
		self.__pq = pq
		self.__a = a
		self.__k = k
	
	
	def __call__(self, xx, *a, **k):
		pass
	
	
	def exec_f(self, fn, *a, **k):
		# if cmd is ans executable object...
		try:
			fn = xx
			r = []
			while True:
				c.fetch()
				r.append(fn(c.fetch.param, *a, **k))
		except StopIteration:
			pass
		return pq(r)
	
	
	def exec_q(self, xx, *a, **k):
		# prepare to search data
		c = Cursor(self.o)
		
	
	def get_qspec(self, string_spec):
		"""
		Pass a string starting with a delimiter such as / forward-slash,
		and separate each path element with that same delimiter. Path
		elements should start with dict key strings (which will match
		regardless of type).
		
		When a path element is "*", the remainder of the search applies
		within all the current element's keys. (It's pretty much as you'd
		expect from fnmatch, but in a loop.)
		"""
		d = string_spec[0]
		return string_spec[1:].split(d)
	
	
	
	
	
	
	"""
	def alternate_possibilities(self):
		# alternately, args could be a string such as one accepted
		# by trix.util.dq (data query), but with string substitutions
		# such as '*' asterisk for "any value".
		
		if isinstance(xx, list):
			query = xx
		
		elif a:
			# if *a exists, there's more than one argument, so it's
			# not a 0-delimited string...
			query = [xx]
			query.extend(a)
			
		# check for delimited beginning (splitting on  first char)
		elif isinstance(xx, str) and xx:
			query = xx[1:].split(xx[0])
		
		else:
			raise ValueError("invalid-params", xdata(cmd=xx, args=a))
		
		return query
	"""
	
	
	"""
	def other_weirdness:
			n = trix.ncreate('x.nav.Nav')
			c = type(self.o) # create new instance of the type self.o
			for item in query:
				if item=='*':
					for d in n.s:
						# for now, all begining path elements must be covered
						
	def xoxo(self, xx, *a):
		pass
	"""



