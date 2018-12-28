#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ... import *
from ...util.enchelp import *
from ...util.linedbg import *

PLUG_UPDT = 15 # update plugins every 15 seconds


#
# ---- IRC Functions -----
#
class irc(object):
	"""Common top-level irc classmethods."""
	
	@classmethod
	def bot(cls, botname):
		"""
		Pass a bot name. The named bot config file will be generated on
		first init; subsequent calls will use the saved config. (If you
		Ctrl-c out of the config form, an exception is raised and no bot
		is returned.)
		
		Returns an IRC Bot object.
		
		>>> from trix.net.irc import *
		>>> b = irc.bot("mybot") # expect config entry form on first call
		>>> b.start()
		"""
		return trix.ncreate("net.irc.bot.Bot", botname)
	
	
	@classmethod
	def config(cls, config, **k):
		"""
		Pass config dict or string path to config json file. Connects to 
		IRC network and returns an IRCConnect object (see below).
		"""
		
		# get configuration
		if isinstance(config, str):
			conf = trix.path(config).wrapper(encoding='utf_8').read()
			conf = trix.jparse(conf)
		elif isinstance(config, dict):
			conf = config
		else:
			raise ValueError("err-invalid-config", xdata(
					detail="bad-config-type", 
					require1=['dict','json-file-path'],
					Note="Requires a dict or string path to json file"
				))
				
		return conf



