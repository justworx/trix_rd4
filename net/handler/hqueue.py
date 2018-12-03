#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import * # Handler
from ...util.lineq import *


class HandleQueue(Handler):
	"""Allows the main process to "handle" the remote process."""
	
	#
	# Remote processes can contact the process server to create a way
	# for the main process to read from and write to them.
	#
	# REMEMBER!
	#  - This class resides in the main process, allowing access to and
	#    control of the remote process.
	#

	def __init__(self, *a, **k):
		"""Pass encoding-related parameters. Default: DEF_ENCODE."""
		Handler.__init__(self, *a, **k)
		self.__q = trix.ncreate('util.xqueue.Queue')
	
	
	#
	# ----------------------------------------------------------------
	# 
	# WE NEED SOME LOGGING IN HERE...
	#
	# ----------------------------------------------------------------
	#
	
	
	
	@property
	def q(self):
		"""Use handler.q to read directly from the queue."""
		return self.__q
	
	
	
	#
	# READ
	#
	def read(self):
		"""Return all queued lines, plus the fragment."""
		
		# create a Buffer
		b = trix.ncreate('util.stream.buffer.Buffer', **self.ek)
		
		# write text from each queue item to the buffer
		while line:
			w.write(L)
		
		# return the full contents of the buffer
		return b.read(**self.ek)
	
	
	
	#
	# HANDLE DATA
	#
	def handledata(self, data):
		"""Queue data for retreival by the main process."""
		if data:
			self.__q.put(data)
		


