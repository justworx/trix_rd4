#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from . import *


class IRCAction(IRCPlugin):
	"""Info collected from various commands."""
	
	connected = False
	
	def __init__(self, pname, bot, config=None, **k):
		IRCPlugin.__init__(self, pname, bot, config, **k)
		self.on_connect = self.config.get("on_connect")
	
	
	def handle(self, e):
		
		# respond to invitations
		if e.irccmd == "INVITE":
			if self.authorize(e):
				self.bot.writeline("JOIN %s" % e.argv[0])
		
		# end motd - connect commands (join)
		elif not self.connected:
			#
			# CONNECTION COMMANDS
			#  - 376 = End MOTD
			#  - 422 = No MOTD file found
			#
			if e.irccmd in ['376', '422']:  
				for cmd in self.on_connect:
					self.bot.writeline(cmd)
				self.connected = True

