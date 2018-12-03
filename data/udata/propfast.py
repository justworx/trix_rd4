#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .mapfast import *


#
# PROPFAST
#  - Fast property lookups.
#
class propfast(mapfast):
	"""Fast codepoint property lookup."""
	
	def __init__(self):
		"""Build the index."""
		mapfast.__init__(self, PROPERTIES)
	
	
	def get(self, c):
		"""Loop through each property list for `c` property matches."""
		rr = [] # collect results
		for r in iter(self.propgen(c)):
			rr.append(r)
		return rr
