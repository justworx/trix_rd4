#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from . import FormatBase


class Format(FormatBase):
	"""Format with the built-in string.format() method."""
	
	def __init__(self, formatString):
		"""
		Pass a format string for the built-in string.format() method. 
		When passed text, this object's format() method will convert it
		to
		"""
		FormatBase.__init__(self)
		self.__formatstr = formatString
	
	
	def format(self, *a, **k):
		"""
		Pass args and kwargs - the values to be formatted into the format
		method of the `formatString` given to the constructor.
		
		f = Format('{0}, {1}, {2}')
		print (f.format('a', 'b', 'c'))
		"""
		return self.__formatstr.format(*a, **k)



