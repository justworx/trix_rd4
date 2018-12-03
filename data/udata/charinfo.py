#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import unicodedata
from ..udata import *
from ...util.xiter import *

class charinfo(xiter):
	"""Provides extended information for current unicode character."""

	def __init__(self, iterable_text):
		"""Pass unicode text, iter, or generator."""
		self.debug_text = iterable_text
		xiter.__init__(self, iter(iterable_text))
		self.o = 0
		self.c = None

	def __next__(self):
		try:
			self.c = xiter.__next__(self)
			self.o += 1
			return self
		except TypeError:
			raise TypeError(xdata(
					itertext=self.debug_text, itertype=type(self.debug_text)
				))

	def __str__(self):
		"""Return the current character as a string."""
		return self.c
	
	def __repr__(self):
		char = "'%s'" % self.c if self.c else "None"
		return "<charinfo %s>" % char
	
	
	# ----------------------------------------------------------------
	# UNICODE DATA
	# ----------------------------------------------------------------
	@property
	def name(self):
		"""Return unicodedata.name."""
		try:
			return unicodedata.name(self.c)
		except:
			return ''

	@property
	def decimal(self):
		"""Return unicodedata.decimal."""
		try:
			return unicodedata.decimal(self.c)
		except ValueError:
			return None

	@property
	def digit(self):
		"""Return unicodedata.digit."""
		try:
			return unicodedata.digit(self.c)
		except ValueError:
			return None

	@property
	def numeric(self):
		"""Return unicodedata.numeric."""
		try:
			return unicodedata.numeric(self.c)
		except ValueError:
			return None

	@property
	def category(self):
		"""Return unicodedata.category."""
		try:
			return unicodedata.category(self.c)
		except ValueError:
			return ''

	@property
	def bidirectional(self):
		"""Return unicodedata.bidirectional."""
		return unicodedata.bidirectional(self.c)

	@property
	def combining(self):
		"""Return unicodedata.combining."""
		return unicodedata.combining(self.c)

	@property
	def east_asian_width(self):
		"""Return unicodedata.east_asian_width."""
		return unicodedata.east_asian_width(self.c)

	@property
	def mirrored(self):
		"""Return unicodedata.mirrored."""
		return unicodedata.mirrored(self.c)

	@property
	def decomposition(self):
		"""Return unicodedata.decomposition."""
		return unicodedata.decomposition(self.c)


	# ----------------------------------------------------------------
	# data.udata
	# ----------------------------------------------------------------
	@property
	def block(self):
		"""Return the name of the block containing this character."""
		return udata.block(self.c)

	@property
	def bracket(self):
		"""Return bracket data."""
		return udata.bracket(self.c)

	@property
	def properties(self):
		"""Return properties associated with this character."""
		return udata.properties(self.c)
	
	@property
	def ord(self):
		"""Ordinal string."""
		s = "%x" % ord(self.c)
		return "0x%s" % s.upper()
	
	
	# ----------------------------------------------------------------
	# ALIASES
	#  - for use in scanquery and in lambdas where space is tight
	# ----------------------------------------------------------------
	@property
	def bidi(self):
		"""Alias for unicodedata.bidirectional."""
		return unicodedata.bidirectional(self.c)
	
	@property
	def cat(self): 
		"""Alias for unicodedata.category."""
		try:
			return unicodedata.category(self.c)
		except:
			return ''
	
	@property
	def num(self):
		"""Alias for unicodedata.numeric."""
		return self.numeric
	
	@property
	def dec(self):
		"""Alias for unicodedata.decimal."""
		return self.decimal
	
	@property
	def dig(self):
		"""Alias for unicodedata.digit."""
		return self.digit
	
	@property
	def props(self):
		"""Alias for udata.properties."""
		return udata.properties(self.c)
	
	@property
	def lend(self):
		"""Alias for self.lineend."""
		return self.lineend
	
	
	
	# ----------------------------------------------------------------
	# USED INTERNALLY
	#  - Properties in this section are not selectable in udata.query,
	#    but exist for use by trix classes (Eg., Scanner) and certainly
	#    may be useful in query "where" lambdas.
	# ----------------------------------------------------------------
	
	@property
	def quote(self):
		# do the fast checks (bidi, cat) first, then do self.props
		return ((self.bidi=='ON') and (self.cat=='Po') and (
			'Quotation_Mark' in self.props))
	
	@property
	def ss(self):
		"""-1 if subscript; 1 if superscript; zero if neither;"""
		return -1 if self.sub else 1 if self.sup else 0
	
	@property
	def sub(self):
		"""True if subscript."""
		return "SUBSCRIPT" in self.name
	
	@property
	def sup(self):
		"""True if superscript."""
		return "SUPERSCRIPT" in self.name
	
	@property
	def alpha(self):
		"""True for letters."""
		return self.cat in ['Lu','Ll']
	
	@property
	def alphanum(self):
		"""True for digits and letters."""
		return self.cat in ['Lu','Ll','Nd']
	
	@property
	def connector(self):
		"""True for 'underscore' (LOW LINE, TIE) connectors."""
		return self.cat == 'Pc'
	
	@property
	def lineend(self):
		"""True if line-ending character (CR, LF, 0x85)."""
		#
		# TO DO
		#  - This is faster than a real lookup, but might break in future
		#    udb versions. This probably should be fixed.
		#
		return self.c in "\r\n\x85" 
	
	
	
	# ----------------------------------------------------------------
	# DISPLAY FEATURES
	#  - Not usually use these in code, but they can be useful to
	#    lookup the meaning of bidi codes, property aliases, etc...
	# ----------------------------------------------------------------
	
	@property
	def bidiname(self):
		"""Full name expanded from `self.bidirectional` code."""
		return udata.propalias().bidi(self.bidi).get(self.bidi)
	
	@property
	def catname(self):
		"""Full name expanded from `self.category` code."""
		return udata.propalias().cat(self.cat).get(self.cat)
	
	@property
	def br(self):
		"""Alias for linebreak."""
		return udata.linebreak(self.c)
	
	@property
	def brname(self):
		"""Return expanded linebreak name (eg, AL=Alphabetic)."""
		d = udata.propalias().linebreak(udata.linebreak(self.c))
		return d[self.br]
	
	@property
	def comma(self):
		"""True if current character is a comma."""
		return (self.cat == 'Po') and ("COMMA" in self.name)
	
	
	#
	# Whitespace Detectors.
	#  - I don't understand '\x0b' - is it not a linebreak? When I
	#    print('\x0b') it looks like a linebreak... what to do?
	#
	@property
	def space(self):
		"""True if the current codepoint is 'White_Space'."""
		# do the fast checks (bidi, cat) first, then do self.props
		return (self.bidi=='WS') and (self.cat=='Zs') and (
				'White_Space' in self.props
			)
	
	@property
	def linebreak(self):
		"""
		Return the LineBreak property for the current codepoint.
		"""
		return udata.linebreak(self.c)
	
	@property
	def tab(self):
		"""True if char is a Segment_Separator - eg, a tab."""
		return self.bidi == 'S'
	
	@property
	def sep(self):
		"""True if BIDI is "S" or "B" - eg, spaces and tabs."""
		return self.bidi in ["S", "B"]
	
	@property
	def white(self):
		"""
		True if BIDI is "S", "WS", or "B" - eg, white space, tab, break,
		separator, or linebreak.
		"""
		return self.bidi in ["S", "B", "WS"]
	
	
	
	# ----------------------------------------------------------------
	# INFO
	# ----------------------------------------------------------------
	def info(self):
		"""
		Return a dict with general attributes of the current character.
		"""
		result = dict(
			#
			# from unicodedata module
			#
			name             = self.name,
			decimal          = self.decimal,
			digit            = self.digit,
			numeric          = self.numeric,
			category         = self.category,
			bidirectional    = self.bidirectional,
			combining        = self.combining,
			east_asian_width = self.east_asian_width,
			mirrored         = self.mirrored,
			decomposition    = self.decomposition,

			#
			# from trix.data.udata
			#
			block   = self.block,
			bracket = self.bracket,
			props   = self.props,
			linebreak = self.linebreak,
			
			#
			c = self.c
		)

		return result


	# DISPLAY
	def display(self, value=None, **k):
		"""Display all info on the current character."""

		if value:
			trix.display(value, **k)

		else:
			#
			# Display is all about development/debugging in this class,
			# so I'm going to go ahead and default "sort_keys".
			#
			k.setdefault('sort_keys', True)

			#
			# EXTRA INFO
			#  - Add some extra info, for visual only.
			#  - This is important (at least to me) so I can understand the
			#    codes for bidiname and catname without looking them up
			#    manually.
			#  - When using the `info` property data while processing a
			#    string, I'll use the code rather than the name... I don't
			#    think it's needed for the dict `info()` returns.
			#
			info = self.info()

			bidiname = udata.propalias().bidi(info['bidirectional'])
			if bidiname:
				info['_bidiname'] = bidiname

			catname = udata.propalias().cat(info['category'])
			if catname:
				info['_catname'] = catname
			
			info['linebreak'] = self.br
			info['linebreakname'] = self.brname
			
			info['__char__'] = [str(info['c'])]
			
			# send through trix.display()
			trix.display(info, **k)
