#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ... import * # trix


DEF_FAMILY = 'AF_INET'
DEF_TYPE   = 'SOCK_STREAM'
DEF_PROTO  = 0

SOCK_TIMEOUT = 0.00001 # read/accept timeout
SOCK_CTIMEOUT = 9      # connection timeout


#
# SOCK-CONF
#  - Stores config for all other sock-package classes.
#
class sockconf(object):
	"""Partial class - part of the SockCon and SockServ classes."""
	
	def __init__(self, config=None, **k):
		"""
		Pass config dict, or any params acceptable to `urlparse()`.
		Address info arguments ('family', 'proto', etc...) may also be
		included for socket connection objects.
		"""
		
		# STEP 1 - Get Config.
		try:
			# If config is a dict, update with k.
			config = config or {}
			config.update(k)
			self.__config = config
		except AttributeError:
			# If config is not a dict, parse it and set self.__config to
			# the parsed dict.
			self.__config = {}

	
	@property
	def config(self):
		"""Object configuration, for reference."""
		return self.__config

	@property
	def ctimeout(self):
		"""Returns timeout value."""
		return self.__config.get('ctimeout', SOCK_CTIMEOUT)

	@property
	def family(self):
		"""Returns timeout value."""
		return self.__config.get('family', DEF_FAMILY)

	@property
	def socktype(self):
		"""Returns timeout value."""
		try:
			return self.__socktype
		except:
			if 'socktype' in self.__config:
				self.__socktype = self.__config['socktype']
			elif 'kind' in self.__config:
				self.__socktype = self.__config['kind']
			elif 'type' in self.__config:
				self.__socktype = self.__config['type']
			else:
				self.__socktype = DEF_TYPE
			return self.__socktype

	@property
	def proto(self):
		"""Returns timeout value."""
		return self.__config.get('proto', DEF_PROTO)


