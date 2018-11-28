#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *


JSON_INDENT = DEF_INDENT
JSON_ENCODE = DEF_ENCODE
FORMAT_SEP = '  ' # default separator for Grid/List items


class FormatBase(object):
	"""
	Abstract base formatting class. A FormatBase object is useless as
	a formatter because it has no format() method, but facilitates the
	storage of arguments and keyword args for use when subclasses are
	called to format text.
	"""
	
	def __init__(self, *a, **k):
		self.__a = a
		self.__k = k
	
	@property
	def args(self):
		"""Formatting arguments."""
		return self.__a
	
	@property
	def kwargs(self):
		"""Formatting keyword arguments."""
		return self.__k
	
	def __call__(self, *a, **k):
		"""Formats and returns data."""
		return self.format(*a, **k)
	
	def output(self, *a, **k):
		"""Format and print data."""
		print (self.format(*a, **k))
	
	def compact(self, *a, **k):
		"""Compact formatted data with zlib, then b64."""
		j = self.format(*a, **k)
		try:
			return FormatBase.__ce.compact(j)
		except:
			FormatBase.__ce = trix.nmodule('util.compenc')
			return FormatBase.__ce.compact(j)
	
	# expand compacted bytes
	expand = NLoader('util.compenc', 'expand')



#
# NO FORMAT - format/print as-is
#
class NoFormat(FormatBase):
	"""Prints or returns "as-is" string."""
	
	def format(self, *a, **k):
		"""Return `data` cast as a string."""
		return str(a) if a else ''
	
	def output(self, *a):
		"""Print `data`."""
		print (self.format(*a))
		


#
# Classes
#
Format   = NLoader("fmt.format", "Format")
JDisplay = NLoader("fmt.jformat", "JDisplay")
JCompact = NLoader("fmt.jformat", "JCompact")
JSON     = NLoader("fmt.jformat", "JSON")
List     = NLoader("fmt.grid", "List")
Grid     = NLoader("fmt.grid", "Grid")
Table    = NLoader("fmt.table", "Table")
Lines    = NLoader("fmt.lines", "Lines")



#
# EXPAND
#  - Expand compacted strings to their original form.
#
expand = FormatBase.expand


