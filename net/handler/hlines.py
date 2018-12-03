#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import * # Handler
from ...util.lineq import *


class HandleLines(Handler):
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

		k.setdefault('encoding', DEF_ENCODE)
		Handler.__init__(self, *a, **k)
		
		self.__lineq = LineQueue(**k) # trix.util.lineq
		
		# Steal these methods directly from lineq
		self.readlines = self.__lineq.readlines
		self.readline = self.__lineq.readline
		self.read = self.__lineq.read
	
	
	
	@property
	def q(self):
		"""Use handler.q to read directly from the queue."""
		return self.__lineq.q
	
	@property
	def lineq(self):
		"""The LineQueue object that handles everything."""
		return self.__lineq
	
	@property
	def fragment(self):
		return self.__lineq.fragment
	
	#
	# HANDLE DATA
	#
	def handledata(self, data):
		"""Queue data for retreival by the main process."""
		if data:
			self.__lineq.feed(data)
		
		


