#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from . import *
from trix.net import url


class IRCDict(IRCPlugin):
	"""Info collected from various commands."""
	
	OWL_OUT = "%i: (%s): %s; %s"
	OWL_URL = "https://owlbot.info/api/v2/dictionary/%s?format=json"
	OWL_HDR = {
		"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Encoding" : "gzip, deflate",
		"Accept-Language" : "en-US,en;q=0.5",
		"Connection"      : "keep-alive",
		"DNT"             : "1",
		"Host"            : "owlbot.info",
		"Upgrade-Insecure-Requests" : "1",
		"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
	}
	
	
	def __init__(self, pname, bot, config=None, **k):
		IRCPlugin.__init__(self, pname, bot, config, **k)
		self.q = self.OWL_URL
		self.h = self.OWL_HDR
		
		self.maxd = 4
	
	
	def handle(self, e):
		
		# only handles PRIVMSG 	and NOTICE events
		if not (e.irccmd in ["PRIVMSG","NOTICE"]):
			return
		
		try:
			# handle dictionary lookups
			
			u = None
			r = None
			s = None
			
			if (e.argc > 1) and (e.argv[0].lower() == 'dict'):
				
				u = url.open(self.q % e.argv[1], **self.h)
				r = u.reader()
				r.seek(0)
				ss = r.read()
				
				# decode
				s = ss.decode('utf_8')
				
				defs = trix.jparse(s)
				try:
					i = 0
					for x in range(0,self.maxd):
						i += 1
						dd = defs[x]
						df = dd['definition']
						ps = dd['type']
						ex = dd.get('example', '')
						
						self.reply(e, self.OWL_OUT % (i, ps, df, ex))
						
				except IndexError:
					pass
		
		except BaseException as ex:
			trix.log("dict plugin", str(ex.args),
					u=u, r=r, s=s
				)	
				
	
	
	
	
	
	
