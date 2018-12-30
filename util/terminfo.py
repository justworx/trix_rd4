#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import *

def termsize(height=24, width=80):
	"""
	Returns a list pair of int values for width and height. Pass
	optional defaults integers width and height (default: 24,80).
	"""
	
	try:
		fn = trix.value("shutil.get_terminal_size")
		return list(fn(*a))
	except:
		pass
	
	try:
		fn = trix.value("subprocess.check_output")
		hw = fn(['stty', 'size']).decode().split()
		return [int(hw[0]), int(hw[1])]
	except:
		pass
	
	if a and (len(a)==2):
		return a
	


