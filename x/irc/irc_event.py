#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


import re
from . import *
from ...util.event import *




class IRCEvent(TextEvent):
	"""
	Parses lines of text received from the IRC server. Separates 
	each line into the following properties:
	
	line   : full line as received
	orig   : text portion of line, with formatting
	text   : deformatted text
	target : recipient channel/nick
	prefix : sender's nick!user@[host]
	host   : sender's host
	user   : sender's user
	nick   : sender's nick
	uid    : sender's user@host
	irccmd : the IRC-specific command (eg. NICK, JOIN, etc...)
	"""
	
	REX = re.compile(r'\x03(?:\d{1,2},\d{1,2}|\d{1,2}|,\d{1,2}|)')
	
	@classmethod
	def stripFormat(cls, s):
		"""Strip color/formating codes from text."""
		s = s.replace('\x02', '').replace('\x16', '')
		s = s.replace('\x1f', '').replace('\x1F', '')
		return cls.REX.sub('', s).replace('\x0f', '').replace('\x0F', '')
	
	
	def __init__(self, line_text):
		"""
		Parses a single line of text as received from an irc server and
		populates the appropriate member variables of this object.
		"""
		# always strip the line for irc text
		line = line_text.strip()
		
		# init superclass
		TextEvent.__init__(self, line)
		
		#
		# parse the irc line
		#
		mm = line.split(' ', 3) # split the line
		ML = len(mm)            # get line length
		
		# manipulate the data
		if mm[0][0:1]==':':
			mm[0] = mm[0][1:]
		if ML>2 and mm[2][0:1]==':':
			mm[2] = mm[2][1:]
		if ML>3 and mm[3][0:1]==':':
			mm[3] = mm[3][1:]
		self.mm = mm
		
		# set up properties
		#self.line   = line # full line as received
		self.__orig   = ''   # text portion of line
		self.__text   = ''   # deformatted text
		self.__target = ''   # recipient channel/nick
		self.__prefix = ''   # sender nick!user@[host]
		self.__host   = ''   # irc host
		self.__user   = ''   # irc user
		self.__nick   = ''   # irc nick
		self.__uid    = ''   # user@host (for auth)
		
		self.__irccmd = None # Placeholder for the IRC-specific command
		
		# parse the event text
		if ML>3 and mm[3]:
			self.__text = mm[3]
		if ML == 2:
			self.__text = mm[1]
			self.__irccmd = mm[0]
		else:
			self.__prefix=mm[0]
			x = mm[0].split('!',1)
			if len(x)==1:
				self.__nick=''
				self.__user=''
				self.__host=x[0]
			else:
				self.__nick=x[0]
				x = x[1].split('@',1)
				self.__user=x[0]
				if len(x)>1:
					self.__host=x[1]
			
			if len(mm) > 1:
				self.__irccmd = mm[1]
			else:
				irc.debug(
					"Strange Line", "Strange Command", self.line
					)
			if len(mm) > 2:
				self.__target = mm[2]
			
			self.__uid ='%s@%s' % (self.__user, self.__host)
		
		if self.__text:
			self.__orig = self.__text
			self.__text = self.stripFormat(self.__text)
	
	@property
	def orig(self):
		"""Original text, potentially containing formatting."""
		return self.__orig
	
	@property
	def text(self):
		"""Straight text, with any formatting removed."""
		return self.__text
	
	@property
	def target(self):
		"""recipient channel/nick"""
		return self.__target
	
	@property
	def prefix(self):
		"""sender nick!user@[host]"""
		return self.__prefix
	
	@property
	def host(self):
		"""irc host"""
		return self.__host
	
	@property
	def user(self):
		"""irc user"""
		return self.__user
	
	@property
	def nick(self):
		"""irc nick"""
		return self.__nick
	
	@property
	def uid(self):
		"""user@host (for auth)"""
		return self.__uid
		
	@property
	def irccmd (self):
		"""Placeholder for the IRC-specific command"""
		return self.__irccmd
	
	@property
	def dict(self):
		"""Debugging utility - returns dict."""
		return {
			'line'   : self.line,
			'orig'   : self.orig,
			'text'   : self.text,
			'target' : self.target,
			'prefix' : self.prefix,
			'host'   : self.host,
			'user'   : self.user,
			'nick'   : self.nick,
			'uid'    : self.uid,
			'irccmd' : self.irccmd,
			'argv'   : self.argv,
			'argc'   : self.argc
		}
