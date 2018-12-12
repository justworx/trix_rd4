# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *
from ...urli import *


class Announce(IRCPlugin):
	"""Scan lines for urls and check for embed info (eg, youtube)."""
	
	def __init__(self, pname, bot, config=None, **k):
		IRCPlugin.__init__(self, pname, bot, config, **k)
		keys = config.get('tags')
		self.uu = EmbedInfo(keys)
		self.prior = None
	
	
	
	def handle(self, e):
		
		try:
			# don't let this bot trigger the announcement!
			if e.nick != self.bot.nick:
				targ = e.target
				info = self.uu.query(e.text)
				
				#
				# Remove announcement of url when the url is all that's
				# returned; This prevents duplication of the same line.
				#
				if (info.strip() == e.text.strip()):
					info = None
				
				# and this prevents repeats due to another bot in channel
				elif info == self.prior:
					info = None
				
				if info:
					if len(info) < 200:
						#
						# don't let screwy websites cause the bot to flood by
						# sending super-long text that matches the title regex.
						#
						self.bot.writeline("PRIVMSG %s : -- %s" % (targ, info))
						
						# Set the prior to prevent response to repeats of the
						# url.
						self.prior = info
		except:
			if not self.is_channel_name(e.target):
				self.reply(e, xdata(err="URLInfo Lookup Fail"))
			pass
	

