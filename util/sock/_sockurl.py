#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from ._sockconf import * # trix
from ..urlinfo import *


class sockurl(sockconf):
	"""Properties of a socket related to a given url."""
	
	def __init__(self, config=None, **k):
		"""Pass args as expected by `trix.util.urlinfo`."""
		
		# STEP 1 - process config.
		try:
			try:
				#
				# If `config` is given as a dict, update it with the given
				# kwargs and create a urlinfo object.
				#
				config.update(k)
				self.__urlinfo = urlinfo(**config)
				sockconf.__init__(self, config)
			
			except AttributeError:
				#
				# Otherwise, if `config` is not a dict, it had better be 
				# something urlinfo can parse. Acceptable non-dict `config` 
				# arguments are tuple (host,port), int (port, with default
				# host), or string url.
				#
				self.__urlinfo = urlinfo(config, **k)
				sockconf.__init__(self, self.__urlinfo.dict, **k)		
		
		except Exception as ex:
			try:
				ui = self.__urlinfo
			except:
				ui = None
			raise type(ex)(ex.args, xdata(error='err-init-fail', k=k,
					require='config-url-params', config=config, urlinfo=ui
				))
	
	@property
	def url(self):
		"""The urlinfo object."""
		return self.__urlinfo
	
	# ADDR-INFO
	def addrinfo(self, **k):
		"""Address info object, from urlinfo."""
		return self.__urlinfo.addrinfo(**k)
