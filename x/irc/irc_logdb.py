#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
# 

#
# UNDER CONSTRUCTION! 
#  - This file is totally under construction, just getting started,  
#    and does pretty much nothing at the moment except create itself.
#  - There are almost certainly bugs.
#


from ...data.database import *


IRC_LOGDB_NCONFIG = "net/irc/config/logdb.conf"


class IRCLogDB(Database):
	"""Manages the IRC Log Database."""
	
	def __init__(self, *a, **k):
		"""
		Pass any args/kwargs if necessary (probably not). Do not pass
		the config file path - that's defined by IRC_LOGDB_NCONFIG.
		
		>>> ircdb = IRCLogDB()
		>>> ircdb.open()
		>>> ircdb.addbot("mybot")
		"""
		
		confpath = k.get('configpath', IRC_LOGDB_NCONFIG)
		
		# load the config file path
		config = trix.nconfig(confpath)
		
		# init the superclass (Database)
		if not a:
			a = [config]
		Database.__init__(self, *a, **k)
		

	#	
	# BOT
	#	
	def addbot(self, botname):
		"""Add new bot record with given botname."""
		self.opq("addbot", (botname,))
		self.commit()
	
	def getbot(self, botname):
		"""Return bot record (cursor) given botname."""
		return self.opq("getbot", (botname,))
	
	def getbotid(self, botid):
		"""Return bot record (cursor) given botid."""
		return self.opq("getbotid", (botid,))
	
	def getbots(self):
		"""Return a cursor listing all botnames in alphabetical order."""
		return self.opq("getbots")
	
	
	#	
	# NETWORK
	#	
	def addnet(self, network):
		"""Add new network record with given network name."""
		self.opq("addnet", (network,))
		self.commit()
	
	def getnet(self, network):
		"""Return network record (cursor) given network name."""
		return self.opq("getnet", (network,))
	
	def getnetid(self, netid):
		"""Return bot record (cursor) given netid."""
		return self.opq("getnetid", (netid,))
	
	def getnets(self):
		"""Return a cursor listing all networks in alphabetical order."""
		return self.opq("getnets")
	
	
	#	
	# NICK
	#	
	def addnick(self, nick):
		self.opq("addnick", (nick,))
		self.commit()
	
	def getnick(self, nick):
		"""Return nick record (cursor) given nick name."""
		return self.opq("getnick", (nick,))
	
	def getnickid(self, nickid):
		"""Return bot record (cursor) given nickid."""
		return self.opq("getnickid", (nickid,))
	
	def getnicks(self):
		"""Return a cursor listing all nicks in alphabetical order."""
		return self.opq("getnicks")
	
	
	#	
	# CHAN
	#	
	def addchan(self, channel):
		self.opq("addchan", (channel,))
		self.commit()
	
	def getchan(self, channel):
		"""Return chan record (cursor) given chan name."""
		return self.opq("getchan", (channel,))
	
	def getchanid(self, chanid):
		"""Return bot record (cursor) given chanid."""
		return self.opq("getchanid", (chanid,))
	
	def getchans(self):
		"""Return a cursor listing all chans in alphabetical order."""
		return self.opq("getchans")
	
	
	#
	# USER
	#
	def adduser(self, user):
		self.opq("adduser", (user,))
		self.commit()
	
	def getuser(self, user):
		"""Return user record (cursor) given user name."""
		return self.opq("getuser", (user,))
	
	def getuserid(self, userid):
		"""Return bot record (cursor) given userid."""
		return self.opq("getuserid", (userid,))
	
	def getusers(self):
		"""Return a cursor listing all users in alphabetical order."""
		return self.opq("getusers")
	
	
	#
	# MASK
	#
	def addmask(self, mask):
		self.opq("addmask", (mask,))
		self.commit()
	
	def getmask(self, mask):
		"""Return mask record (cursor) given mask name."""
		return self.opq("getmask", (mask,))
	
	def getmaskid(self, maskid):
		"""Return bot record (cursor) given maskid."""
		return self.opq("getmaskid", (maskid,))
	
	def getmasks(self):
		"""Return a cursor listing all masks in alphabetical order."""
		return self.opq("getmasks")
	
	
	#
	# NAME
	#
	def addname(self, name):
		self.opq("addname", (name,))
		self.commit()
	
	def getname(self, name):
		"""Return name record (cursor) given name name."""
		return self.opq("getname", (name,))
	
	def getnameid(self, nameid):
		"""Return bot record (cursor) given nameid."""
		return self.opq("getnameid", (nameid,))
	
	def getnames(self):
		"""Return a cursor listing all names in alphabetical order."""
		return self.opq("getnames")
	
	
	#
	# ID
	#
	def addid(self, netid, nickid, userid, maskid, nameid=''):
		"""
		
		 THIS METHOD IS UNDER CONSTRUCTION!
		IT WILL PROBABLY CHANGE DRASTICALLY!
		   DANGER WILL ROBINSON! DANGER!
		
		#
		# MAYBE....
		# This should be getid() and it should automatically add the
		# relevant details if that combination doesn't yet exist.
		#
		# ALSO....
		# I'm not too sure what to do about nameid yet... might need
		# to rethink some of this.
		#
		"""
		self.open_addid(self, netid, nickid, userid, maskid, nameid)
		self.commit()
	
	
	def open_addid(self, netid, nickid, userid, maskid, nameid=''):
		"""Call this once if gathering WHO info... commit afterward!"""
		self.opq("addid", (
				netid, nickid, userid, maskid, nameid, time.time()
			))
	
	
	#
	# CHAT
	#
	def addchat(self, can_i_pass_an_event_here_qm):
		pass
	
	"""
		"addid"   : "insert into identity values (?,?,?,?,?,?)",
		"addchat" : "insert into chatlog values (?,?,?,?,?)",
		
		"netid" : "select netid from network where network = ?",
		"chanid" : "select chanid from channel where channel = ?",
		"nickid" : "select nickid from nickname where nickname = ?",
		"userid" : "select userid from username where username = ?",
		"maskid" : "select maskid from hostmask where hostmask = ?"
	"""
	



#
# ----- TEST SCRIPT ------------------------------------------------
# 

if __name__ == '__main__':

	from trix.fs import *
	
	db = IRCLogDB(path="~/dev/trix/net/irc/test.sqlite3")
	try:
		FileBase(db.path).remove()
	except FileNotFoundError:
		pass
	
	db.open()
	
	#print ("path:", db.path)
	
	
	#	
	# BOT
	#	
	db.addbot('trixie')
	if not db.getbot('trixie').fetchall() == [(1, 'trixie')]:
		raise Exception('getbot', xdata())
	if not db.getbotid(1).fetchall() == [(1, 'trixie')]:
		raise Exception ('getbotid', xdata())
	if not db.getbots().fetchall() == [(1, 'trixie')]:
		raise Exception ('getbots', xdata())
	print ("bot: OK")
	
	#	
	# NETWORK
	#	
	db.addnet("somenet")
	if not db.getnet('somenet').fetchall() == [(1, 'somenet')]:
		raise Exception('getnet', xdata())
	if not db.getnetid(1).fetchall() == [(1, 'somenet')]:
		raise Exception ('getnetid', xdata())
	if not db.getnets().fetchall() == [(1, 'somenet')]:
		raise Exception ('getnets', xdata())
	print ("net: OK")
	
	
	#	
	# NICK
	#	
	db.addnick('nickname')
	if not db.getnick('nickname').fetchall() == [(1, 'nickname')]:
		raise Exception('getnick', xdata())
	if not db.getnickid(1).fetchall() == [(1, 'nickname')]:
		raise Exception ('getnickid', xdata())
	if not db.getnicks().fetchall() == [(1, 'nickname')]:
		raise Exception ('getnicks', xdata())
	print ("nick: OK")
	
	
	#	
	# CHAN
	#	
	db.addchan('channel')
	if not db.getchan('channel').fetchall() == [(1, 'channel')]:
		raise Exception('getchan', xdata())
	if not db.getchanid(1).fetchall() == [(1, 'channel')]:
		raise Exception ('getchanid', xdata())
	if not db.getchans().fetchall() == [(1, 'channel')]:
		raise Exception ('getchans', xdata())
	print ("chan: OK")
	
	
	#	
	# USER
	#	
	db.adduser("someuser")
	if not db.getuser('someuser').fetchall() == [(1, 'someuser')]:
		raise Exception('getuser', xdata())
	if not db.getuserid(1).fetchall() == [(1, 'someuser')]:
		raise Exception ('getuserid', xdata())
	if not db.getusers().fetchall() == [(1, 'someuser')]:
		raise Exception ('getusers', xdata())
	print ("user: OK")
	
	
	#
	# MASK
	#
	db.addmask("somemask")
	if not db.getmask('somemask').fetchall() == [(1, 'somemask')]:
		raise Exception('getmask', xdata())
	if not db.getmaskid(1).fetchall() == [(1, 'somemask')]:
		raise Exception ('getmaskid', xdata())
	if not db.getmasks().fetchall() == [(1, 'somemask')]:
		raise Exception ('getmasks', xdata())
	print ("mask: OK")
	
	
	#
	# NAME
	#
	db.addname("somename")
	if not db.getname('somename').fetchall() == [(1, 'somename')]:
		raise Exception('getname', xdata())
	if not db.getnameid(1).fetchall() == [(1, 'somename')]:
		raise Exception ('getnameid', xdata())
	if not db.getnames().fetchall() == [(1, 'somename')]:
		raise Exception ('getnames', xdata())
	print ("name: OK")
	
	
	#
	# Can't add ID and CHAT until i figure out how to actually *do*
	# ID and CHAT.
	#



