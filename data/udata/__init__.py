#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
# 
# Thanks, jotun, for the speed boost on linebreak properties.
#

from ... import *
from .blocks import BLOCKS
from .brackets import BRACKETPAIRS
from .proplist import PROPERTIES
import bisect



class udata(object):
	
	CTime = 30
	CSize = 512*2
	
	
	#
	# BRACKETS
	#
	@classmethod
	def bracket(cls, c):
		"""
		Tuple with open/close indicator and the bracket matching `c`.
		
		# EXAMPLE:
		>>> udata.bracket('(')
		('o', ')')
		"""
		i = ord(c)
		x = bisect.bisect_left(BRACKETPAIRS, [i])
		try:
			BP = BRACKETPAIRS[x]
			return (BP[2], unichr(BP[1])) if (BP and BP[0]==i) else None
		except IndexError:
			return None
	
	
	
	#
	# BLOCKS
	#
	@classmethod
	def block(cls, c):
		"""
		Name of the block containing char `c`.
		
		# EXAMPLE:
		>>> udata.block('c')
		'Basic Latin'
		"""
		i = ord(c)+1
		x = bisect.bisect_left(BLOCKS, [[i]])
		B = BLOCKS[x-1]
		return B[1]
	
	@classmethod
	def blocks(cls):
		"""Dict with block-name keys and range list values."""
		try:
			return cls.__blocks
		except AttributeError:
			cls.__blocks = {}
			cls.__blocknames = []
			for b in BLOCKS:
				cls.__blocknames.append(b[1])
				cls.__blocks[b[1]] = b[0]
			return cls.__blocks

	@classmethod
	def blocknames(cls):
		"""List of all blocknames."""
		try:
			return cls.__blocknames
		except AttributeError:
			cls.blocks() # calling blocks sets self.__blocknames 
			return cls.__blocknames
	
	
	
	#
	# PROPERTIES
	#
	@classmethod
	def propfast(cls):
		"""Returns an object that looks up properties fast."""
		try:
			return cls.__propfast
		except AttributeError:
			cls.__propfast = trix.ncreate('data.udata.propfast.propfast')
			return cls.__propfast
	
	@classmethod
	def breakfast(cls):
		"""Returns an object that looks up linebreak properties fast."""
		try:
			return cls.__breakfast
		except AttributeError:
			cls.__breakfast = trix.ncreate('data.udata.breakfast.breakfast')
			return cls.__breakfast
	
	@classmethod
	def properties(cls, c):
		"""List of all properties of the given char `c`."""
		return cls.propfast().get(c)
	
	# PROP-ALIAS
	@classmethod
	def propalias(cls):
		"""Return a propalias object."""
		try:
			return cls.__propalias
		except AttributeError:
			cls.__propalias=trix.nvalue('data.udata.propalias','propalias')
			return cls.__propalias
	
	# LINE-BREAK PROPERTY (CODE)
	@classmethod
	def linebreak(cls, c):
		return cls.breakfast().get(c)
		#linebreak = trix.nmodule('data.udata.linebreak')
		#return linebreak.find_linebreak_property(ord(c))
	
	
	
	#
	# QUERY
	#
	@classmethod
	def query(cls, **k):
		"""
		The query() function can help us find the information we need to 
		build efficient scanning methods.
		
		The idea is to select charinfo properties (eg., category, props, 
		etc...) that match keyword argument specifications. Results are
		printed to the terminal as a grid.
		
		KWARGS:
		 * select : A list of `charinfo` properties to select.
		            Eg, select="char numeric decimal digit" 
		 * blocks : A list of blocks to query. 
		            Eg, blocks=['Basic Latin', 'Gothic']
		 * where  : A callable object that returns True for objects that 
		            should be selected, else False.
		            Eg, where=lambda c: c.numeric != None
		 
		 * text   : The `text` kwarg may be specified instead of 'blocks'
		            to query info from a given string (or other iterable).
		            Eg, text="Text I'm having trouble parsing!" 
		
		Either `blocks` or `text` may be specified, not both. If neither 
		is specified, all codepoints are checked for matches.
		
		```python3
		from trix.data.scan.scanquery import *
		query(
		    select="block char numeric decimal digit",
		    blocks=['Basic Latin', 'Gothic'],
		    where =lambda c: c.num != None 
		  )
	
		```
		
		The complete list of property names is:
		[
			'char', 'c', 'block', 'bidi', 'bidirectional', 'bracket', 'cat',
			'category', 'num', 'numeric', 'dec', 'decimal', 'dig', 'digit',
			'name', 'props', 'properties', 'bidiname', 'catname', 'ord'
		]
		
		Several of these are aliases (a space-saving measure for lambdas):
		 - bidi = bidirectional
		 - cat = category
		 - char = c
		 - dec = decimal
		 - dig = digit
		 - num = numeric
		 - props = properties
		
		"""
		return trix.ncreate('data.udata.query.query', **k)

