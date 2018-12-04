#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from ...util.enchelp import *


class Plugin(EncodingHelper):
	"""Base plugin class."""
	
	#
	# INIT
	#
	def __init__(self, pname, owner, config=None, **k):
		"""
		The most basic Plugin object, on which other plugins will be
		based. This class is not a plugin itself, but implements methods
		common to all subclasses.
		
		Args:
		 * String `pname` a unique identifier for the owner's set of
		   plugin objects. The `pname` generally matches the name of
		   a plugin's module, but that's only convention. You can pass
		   any string you like as its unique.
		 * Object `owner`, which holds and controls this plugin.
		 * A config dict for this plugin.
		"""
		self.__created = time.time()
		
		self.__config = config or {}
		self.__config.update(k)
		
		self.__pname = pname
		self.__owner = owner
		self.__debug = self.__config.get('debug', 0)
		
		EncodingHelper.__init__(self, self.__config)
	
	
	@property
	def created(self):
		return self.__created
	
	@property
	def name(self):
		return self.__pname
	
	@property
	def owner(self):
		return self.__owner
	
	@property
	def config(self):
		return self.__config
	
	@property
	def debugging(self):
		return self.__debug
	
	
	#
	# AUTHORIZATION
	#  - Base auth has no authorization scheme atm. Such may be added
	#    in the future, but if so, will require active enabling. In
	#    other words, and future auth changes here will require some 
	#    assertion on your part to enable.
	#  - As this level of plugin is intended for use with the Console
	#    class, it is not (and probably will not become) necessary.
	#  - Note, however, that some subclass plugins will automatically
	#    have an auth scheme suited to their purpose.
	#
	def authorize(self, e):
		"""Returns True."""
		return True
	
	
	#
	# REPLY
	#
	def reply(self, e, data):
		"""Set event object's `e.reply` to the given `data` value."""
		e.reply = data
	
	
	#
	# HANDLE EVENT
	#
	def handle(self, e):
		"""
		Plugins may override this to handle whatever action is
		indicated by `event`.
		"""
		if e.argc and self.authorize(e):
			if e.argvl[0] == 'created':
				self.reply(str(self.__created))
		
		return "command-invalid"
	
	
	#
	# ERROR
	#
	def error(self, e, *a, **k):
		"""
		Set the error response indicating that active processing of an
		event - one expected by the processing object to complete the 
		job - has resulted in an unresolvable error which should likely
		be reported to the user.
		
		Pass any number of args and kwargs; xdata() is automatically
		appended.
		"""
		e.error = [a, k, xdata()]
		
	
	
	#
	# DEBUG
	#
	def debug(self, *a, **k):
		"""Prints a line-debug message."""
		if self.debugging:
			linedbg().dbg(*a, **k)
	
	
	

