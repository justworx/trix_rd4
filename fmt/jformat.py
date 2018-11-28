#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *
from ..util.xjson import *  # json, JSONDisplay

# JSON FORMAT
class JSON(FormatBase):
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('cls', JSONDisplay)
		FormatBase.__init__(self, **k)
	
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)



#
# JSON DISPLAY - Big, pretty, and readable.
#
class JDisplay(JSON):
	"""JSON in a more human-readable, display format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('indent', JSON_INDENT)
		JSON.__init__(self, **k)
	
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)





#
# JSON FORMAT - Tight as possible; for transmission/storage.
#
class JCompact(JSON):
	"""Compact JSON format. Unneeded spaces removed."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('separators', (',',':'))
		JSON.__init__(self, **k)

	def format(self, data):
		"""Format as compact json; no unnecessary white space."""
		return ''.join(json.dumps(data, **self.kwargs).splitlines())

