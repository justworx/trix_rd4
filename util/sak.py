#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import sys


def modlist(**k):
	"""
	List loaded modules (with optional filters). Good for	debugging.
	
	FILTERS (by keyword argument) are cumulative.
	 * prefix : results must start with prefix.
	 * suffix : results must end with suffix.
	 * contains: results must contain the given kwarg's value.
	"""	
	keys = sorted(sys.modules.keys())
	fstr = " * {:<25} : {}"
	
	for key in keys:
		
		show = True
		if k.get('prefix'):
			show = show and key.startswith(k.get('prefix'))
		if k.get('suffix'):
			show = show and key.endswith(k.get('suffix'))
		if k.get('contains'):
			show = show and k.get('contains')
		
		# display (if filters did not prevent)
		if show:
			print(fstr.format(key, sys.modules[key]))

