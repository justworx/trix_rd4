#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from json import *


class JSONDisplay(JSONEncoder):
	# Handles unparsable types by returning their representation to be
	# stored as a string.
	
	def default(self, obj):
		try:
			return JSONEncoder.default(self, obj)
		except:
			try:
				return repr(obj)
			except:
				return "<%s>" % obj.__class__.__name__

