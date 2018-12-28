#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *
from ....util.matheval import *
from ....util.compenc import *
from ....util.convert import *

class IRCCalc(IRCPlugin):
	"""Useful commands for controlling the bot via privmsg/notify."""
	
	def istempc(self, a1):
		if len(a1)==3:
			a=a1.lower()
			if (a[0] in 'fkc') and (a[2] in 'fkc') and (a[0]!=a[2]):
				return a[1]=='2'
	
	#
	# HANDLE
	#
	def handle(self, e):
		
		# only handles PRIVMSG 	and NOTICE events
		if not (e.irccmd in ["PRIVMSG","NOTICE"]):
			return 
		
		cmd = e.argvl[0]
		if not cmd.strip():
			return
		
		try:
			args = " ".join(e.argvl[1:])
			
			# MATH
			if cmd in ['calc', 'calculate']:
				self.reply(e, str(matheval(args)))
			
			# CONVERT
			elif self.istempc(cmd):
				ctemp = Convert().temp(cmd[2], cmd[0], float(e.argv[1]))
				self.reply(e, str(ctemp)+cmd[2].upper())
			
			# BASE-64/32/16
			else:
				enc = self.bot.encoding
				try:
					if (cmd[0]=='b') and (cmd[1] in "631"):
						spx = e.text.split(' ', 1) # get all but the first word
						bts = spx[1].encode(enc)   # encode it to bytes
						if cmd == 'b64':
							self.reply(e, b64.encode(bts).decode(enc))
						elif cmd == 'b64d':
							self.reply(e, b64.decode(bts).decode(enc))
						elif cmd == 'b32':
							self.reply(e, b32.encode(bts).decode(enc))
						elif cmd == 'b32d':
							self.reply(e, b32.decode(bts).decode(enc))
						elif cmd == 'b16':
							self.reply(e, b16.encode(bts).decode(enc))
						elif cmd == 'b16d':
							self.reply(e, b16.decode(bts).decode(enc))
				except IndexError:
					pass
				
		except Exception as ex:
			typ = str(type(ex))
			err = str(ex)
			trix.log("command plugin error", typ, err)
			
			#
			# Let's not send this back unless it's pvt to owner
			#
			#msg = "%s: %s" % (typ, err)
			#self.reply(e, msg)
			#
		