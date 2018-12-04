#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from . import *
import time

class portscan(cline):
	"""
	Scan local ports. This may take several seconds.
	"""
	def __init__(self):
		t = time.time()
		print ("Scanning local ports...")
		n = trix.ncreate('util.network.Host')
		r = n.portscan() 
		trix.display(r)
		print ("scan-time:", time.time()-t)
