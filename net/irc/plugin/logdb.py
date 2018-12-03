#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

#####    ---    UNDER CONSTRUCTION!    ---    #####

from . import *

class LogDB(IRCPlugin):
	"""Log IRC chat to a database."""
	
	def __init__(self, pname, bot, config=None, *a, **k):
		
		# init superclass; sort out config
		IRCPlugin.__init__(self, pname, bot, config, *a, **k)
		
		# get a service connection
		services = trix.ncreate("app.service.Services")
		self.__con = services.connect('irclog')
		
		# make sure it's open - ignore "already-open" errors; more 
		# serious errors would show up later here in init
		self.__con('open')
		
		# make sure the current network is in the database
		e = self.__con('getnet', bot.network)
		e = self.__con('fetchn', e.reply)
		try:
			if e.reply:
				replylist = e.reply[0]
				self.__netid = replylist[0]
		except:
			#
			# sleepy! gotta call it a night
			# TEST THE FOLLOWING...........................
			#
			e = c.addnet(bot.network)
			replylist = e.reply[0]
			self.__netid = replylist[0]
			
			
		
		"""
		# create the database object
		dbconfig = trix.nconfig("net/irc/config/logdb.conf")
		self.__db = trix.ncreate("data.database.Database", dbconfig)
		"""
	
	
	
	def handle(self, e):
		
		cmd = e.argvl[0]
		if cmd == 'test':
			self.reply(e, "Pass")
		
	
