#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from .. import *


class IRCPlugin(EncodingHelper):
	"""Base IRC plugin."""

	def __init__(self, pname, bot, config=None, **k):
		
		# store the bot object
		self.bot = bot
		
		# set default for this objects bot.ginfo dict
		bot.ginfo.setdefault(pname, {})
		
		# store the current dict as `self.info`
		self.info = bot.ginfo[pname]
		
		# setup config and encoding-related args
		self.config = config or {}
		self.config.update(k)
		EncodingHelper.__init__(self, self.config)
		
		# save create time
		self.created = time.time()
	
	
	#
	# AUTHORIZATION
	#  - Currently, only hostmasks in the 'owner' list (as set by
	#    config) can control the bot via PRIVMSG/NOTICE.
	#
	def authorize(self, e):
		if e.nick != self.bot.nick:
			return e.host in self.bot.owner
		return False
	
	
	def reply(self, e, text):
		"""
		Reply `text` to the user or channel that sent event `e`.
		"""
		if text and (e.irccmd in ["PRIVMSG", "NOTICE"]):
			if self.is_channel_name(e.target):
				self.bot.writeline("%s %s :%s" % (e.irccmd, e.target, text))
			else:
				self.bot.writeline("%s %s :%s" % (e.irccmd, e.nick, text))
	
	
	def handle(self, e):
		"""
		Plugins may override this to handle whatever action is
		indicated by `event`.
		"""
		if e.argv[0] == 'about':
			self.reply(e, "Plugin. Created: %s", str(self.created))
	
	
	def update(self):
		"""
		Plugins may override this to handle any maintenance activities;
		It's called periodically as set in config.
		"""
		pass

	
	def is_channel_name(self, text):
		"""
		Every event is targeted either to a channel or a nick. This
		method returns True if it's a channel, else False.
		"""
		try:
			return text[0] in self.bot.chantypes
		except:
			return text[0] == '#'
