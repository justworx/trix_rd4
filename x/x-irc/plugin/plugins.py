#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *


class Plugins(IRCPlugin):
	"""List, load, unload, reload plugins."""
	
	def handle(self, e):
		"""
		User PRIVMSG or NOTICE to send 'plugin' commands. Available
		commands are: 'list', 'load', 'unload', and "reload".
		"""
		if not self.authorize(e):
			pass
			
		elif e.irccmd in ["PRIVMSG", "NOTICE"]:
			
			# if command is 'plugin'...
			arg0 = e.argv[0].lower()
			if (e.argc>1) and (arg0 in ['plugin', 'plugins']):
				
				# lowercase the first argument
				arg1 = e.argv[1].lower()
				if arg1 == 'list':
					self.reply(e, " ".join(self.bot.plugins.keys()))
				else:
					argx = e.argv[2:] # plugin cmd <plugin list>
					
					# respond to argument 1
					if arg1 == 'reload':
						for p in argx:
							print ("reload 1; plugins.handle;", p)
							self.bot.plugin_reload(p.lower())
					
					elif arg1 in ['add', 'load']:
						for p in argx:
							if not p in self.bot.plugins:
								self.bot.plugin_add(p.lower())
					
					elif arg1 in ['remove', 'unload']:
						for p in argx:
							if p in self.bot.plugins:
								self.bot.plugin_remove(p.lower())
		
			else:
				IRCPlugin.handle(self, e)
