#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from . import *

class version(cline):
	"""
	Print version information.
	"""
	def __init__(self):
		version = dict(
			version   = VERSION,
			copyright = "Copyright (C) 2018 justworx",
			license   = 'agpl-3.0'
		)
		trix.display(version)
	