#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

#
# This class is suboptimal. Use the Cursor class for such queries,
# particularly for parsing large files.
#

from .param import *

class Query(object):
	"""
	This python data Query class is good for exploring data in python
	objects (particularly lists) and files. The `head`, `grid`, and
	`peek` methods let you fine-tune queries to get the results and
	conversions you need.
	
	The pdq module is superceeded by the data.cursor module, which can
	handle large files much faster and more efficiently but lacks the
	exploration tools (head, peek, etc...) of pdq.Query.
	"""

	def __init__(self, data=None, **k):
		"""
		Pass a `data` object (eg, list), or use the 'file' keyword args
		to specify a data file path and encoding. The 'stream' keyword
		argument is also available for reading objects with a read()
		method.
		"""

		# encoding; used only if data is text
		self.__encoding = k.get('encoding', None)
		
		# type specification for row object
		self.__TRow = k.get('row', QRow)
		
		# make sure there's something for data
		self.__data = data = data if data else ''
		
		# allow reading of text or gzip files
		if 'file' in k:
			reader = trix.path(k.pop('file')).reader(**k)
			self.__data = reader.read()
		elif 'stream' in k:
			self.__data = k['stream'].read()
		else:
			self.__data = data
		
		# if 'encoding' is specified, decode bytes only
		if self.__encoding and isinstance(self.__data, pxbytes):
			self.__data = self.__data.decode(self.__encoding)
		
		# prep undo
		self.__undo = self.__data
	
	
	def __getitem__(self, key):
		return self.data[key]
	
	
	@property
	def len(self):
		"""Return self.data length."""
		return len(self.data)
	
	@property
	def type(self):
		"""Return the type of the data object."""
		return type(self.__data)
	
	@property
	def data(self):
		"""Return the data object."""
		return self.__data
	
	@data.setter
	def data(self, d):
		"""
		Set the data object. (Use undo to return to previous selection.)
		"""
		if d == self: raise ValueError('pdq-data-invalid')
		self.__undo = self.__data
		self.__data = d
	
	
	# UTILITY METHODS
	
	
	def head(self, *a):
		"""Return, from the given offset, the given number of lines."""
		x,y = (a[0],sum(a[0:2])) if len(a)>1 else (0, a[0] if a else 9)
		try:
			lines = self.data.splitlines()
			try:
				# unicode
				self.lasthead = 'unicode'
				return '\n'.join(lines[x:y])
			except TypeError:
				# bytes
				self.lasthead = 'bytes'
				return b'\n'.join(lines[x:y])
		except AttributeError:
			try:
				# list
				self.lasthead = 'list'
				return self.data[x:y]
			except:
				# other - something python can turn into a string
				self.lasthead = 'other'
				fmt = trix.ncreate('fmt.JDisplay')
				return fmt(self.data).splitlines()[x:y]
				#return str(self.data).splitlines()[x:y]
	
	
	def peek(self, *a):
		"""Print each line. Same args as head()."""
		h = self.head(*a)
		if isinstance(h, (bytes,basestring)):
			print (h)
		else:
			for l in h:
				print (l)
	
	
	def grid(self, *a, **k):
		"""
		Output a grid. Same args as head(); Kwargs passed to grid.Grid
		constructor.
		"""
		trix.ncreate('fmt.grid.Grid', **k).output(self.head(*a))
	
	def rows(self, *a, **k):
		"""
		Returns a generator of type QRow for matching rows.
		"""
		return self.__TRow.paramgen(self.data, self, *a, **k)
	
	
	#
	# QUERY METHODS - Always return a Query object.
	#
	
	def undo(self):
		"""
		Limited undo; works like the old-fashioned undo - undo twice to
		redo.
		"""
		u = self.__data
		self.__data = self.__undo
		self.__undo = u
		return self
	
	def splitlines(self, *a, **k):
		self.data = self.data.splitlines(*a, **k)
		return self
	
	def select(self, fn=None, *a, **k):
		"""Returns a new Query with a copy of matching records."""
		result = []
		for row in self.rows(*a, **k):
			try:
				result.append(fn(row) if fn else row.v[:])
			except Exception as ex:
				raise type(ex)('callback-fail', xdata(i=row.i, v=row.v,
					python=str(ex))
				)	
		return Query(result)
	
	def sort(self, fn=None, **k):
		"""Sort self.data, by the results of fn if given."""
		fn = k.get('desc', k.get('asc', fn))
		if fn:
			order = []
			for row in self.rows():
				order.append([fn(row), row.v])
			reversed(order).sort() if k.get('desc') else order.sort()
			self.data = map(lambda o: o[1], order)
		else:
			if k.get('desc'):
				self.data = reverse(d)
			else:
				sdata = self.data[:]
				sdata.sort()
				self.data = sdata
		return self
	
	def update(self, fn, *a, **k):
		"""Update matching self.data rows to fn result; Return self."""
		self.__undo = self.select().data
		result = []
		for row in self.rows(*a, **k):
			result.append(fn(row))
		self.data = result
		return self
	
	def delete(self, *a, **k):
		"""
		Delete matching rows from self.data; If no where kwarg, delete all;
		Return self.
		"""
		fn = k.get('where', lambda *a,**k: False)
		k['where'] = lambda *a, **k: not fn(*a, **k) # reverse where...
		
		# ...deletes by selecting and keeping what should NOT be deleted.
		newq = self.select(*a, **k)
		self.data = newq.data
		return self
	
	def each(self, fn, *a, **k):
		"""Execute fn for matching rows."""
		for row in self.rows(*a, **k):
			fn(row)
		return self

			



class QRow(Param):
	"""
	The parameter object passed to callback functions/lambdas.
	"""
	
	@classmethod
	def paramgen(cls, data, caller, *a, **k):
		if isinstance(data, (list, set, tuple)):
			return cls.pgseq(data, caller, *a, **k)
		elif isinstance(data, dict):
			return cls.pgdict(data, caller, *a, **k)
		
	@classmethod
	def pgseq(cls, data, caller, *a, **k):
		where = k.get('where')
		for i,v in enumerate(data):
			x = cls(caller, v, i, *a, **k)
			if (not where) or where(x):
				yield x
			
	@classmethod
	def pgdict(cls, data, caller, *a, **k):
		where = k.get('where')
		for key in data.keys():
			x = cls(caller, data[key], key, *a, **k)
			if (not where) or where(x):
				yield x

	def __init__(self, query, value, item, *a, **k):
		Param.__init__(self, value, item)# no args/kwargs! #, *a, **k)
		self.q = query
	
	def qq(self, v=None, **k):
		"""
		Returns a new Query object giving arg `v` or self.v if `v` is 
		None. Keyword arguments also work, so a file kwarg can load a 
		file (ignoring v and self.v altogether).
		"""
		return Query(v=v if v else self.v, **k)
