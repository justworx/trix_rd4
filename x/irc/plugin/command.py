#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *


class IRCCommand(IRCPlugin):
	"""Useful commands for controlling the bot via privmsg/notify."""
	
	#
	# HANDLE
	#
	def handle(self, e):
		
		# only handles PRIVMSG 	and NOTICE events
		if not (e.irccmd in ["PRIVMSG","NOTICE"]):
			return

		if self.authorize(e):
			result = self.handle_command(e)
			if result:
				self.reply(e, result)
	
	
	
	#
	# HANDLE COMMAND
	#  - actual handling of commands
	#
	def handle_command(self, e):
		
		try:
			cmd = e.argvl[0]
			if cmd == 'join':
				self.bot.writeline("JOIN %s" % e.argv[1])
			elif cmd == 'part':
				if self.is_channel_name(e.argv[1]): # TODO: see below 
					self.bot.writeline("PART %s" % e.argv[1])
			elif cmd == 'quit':
				self.bot.writeline("QUIT :%s" % " ".join(e.argv[1:]))
				self.bot.shutdown()
			elif cmd == 'nick':
				self.bot.writeline("NICK %s" % " ".join(e.argv[1:]))
			elif cmd == 'tell':
				target = e.argv[1]
				message = " ".join(e.argv[2:])
				self.bot.writeline("PRIVMSG %s :%s" % (target, message))
			elif cmd == 'mode':
				self.bot.writeline(" ".join(e.argv[0:]))
			
			# -- all purpose --
			# e.g., do mode +v nick
			elif cmd == 'do':
				self.bot.writeline(" ".join(e.argv[1:]))
			
			# -- channel only --
			elif self.is_channel_name(e.target):
				try:
					if cmd == 'op':
						for nick in L:
							self.bot.writeline("MODE %s +o %s" % e.target, nick)
					elif cmd == 'deop':
						for nick in L:
							self.bot.writeline("MODE %s -o %s" % e.target, nick)
				except:
					trix.log("command plugin - channel-only command failed")
			
			# TEST
			elif cmd == 'test':
				print ("\n -- test: start")
				trix.display(e, str(e.dict))
				
				#self.reply(e, "%s %s" % (e.target, e.nick))
				print (" -- test: end\n")
		
		
		#
		# -- error handling --
		#
		except Exception as ex: 
			
			typ = str(type(ex))
			err = str(ex)
			msg = "%s: %s" % (typ, err)
			
			trix.log("command plugin error", typ, err)
			
			return msg
	
	

