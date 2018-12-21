#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from .hhttp import *


class HTest(HandleHttp):
	"""
	The HTest class exists only as an example for the `cline.http` doc.
	"""
	
	def reply(self, req):
		return self.__doc__

