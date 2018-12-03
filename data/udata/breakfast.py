#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .mapfast import *
from .linebreak import *

#
# BREAKFAST
#  - Fast linebreak lookups.
#
class breakfast(mapfast):
	"""Fast linebreak property lookup."""
	
	def __init__(self):
		"""Build the index."""
		mapfast.__init__(self, LINEBREAK)
	
	
	def get(self, c):
		"""Loop through each property list for `c` property matches."""
		#
		# This uses the mapfast generator to find the first property,
		# then returns it immediately because there can be only one
		# linebreak property per codepoint.
		#
		for r in iter(self.propgen(c)):
			return r
	
		"""
		#
		# Putting this before the call to the generator might speed up
		# full queries without slowing down limited-block queries much.
		# good trade? I DON'T KNOW.
		#
		# VERIFY THE RANGES AGAIN BEFORE TRYING THIS!
		#  - should be able to use a query to verify
		#
		char_code = ord(c)
		if char_code >= 0xE0020:
			if char_code >= 0x10FFFE:
				return ''
			if char_code >= 0xF0000:
				return 'XX'
			else: # >=0xE0020 & <0xF0000
				return 'CN'
		"""
	