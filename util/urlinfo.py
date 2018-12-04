#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

import socket
try:
	import urlparse
except:
	from urllib import parse as urlparse
from .. import * # trix


class urlinfo(object):
	"""Parse input to produce a URL."""
	
	__Keys = """
				scheme username password host port path query fragment
				""".strip().split()
	
	def __init__(self, url=None, **k):
		"""
		Parse `url` (updated with k) and store member values.
		
		Argument `url`, if given, may be:
		 - str   : The full or partial url string
		 - tuple : An address tuple (host,port)
		 - int   : Integer `port` (default host: '')
		 - dict  : A config dict from which relevant keys are taken
		 - None  : Take params only from **k (which is parsed as dict)
		"""
		# set params member
		self.__params = (url, k)
		self.__defhost = k.pop('defhost', '')
		
		# get parsed url param dict
		self.__dict = {}
		try:
			self.__uparsestr()
		except:
			self.__parse()
		
		# urlinfo object should behave like a dict, but have all its
		# properties and public methods exposed.
		self.get = self.__dict.get
		self.update = self.__dict.update
		self.setdefault = self.__dict.setdefault
	
	
	
	
	def __str__(self):
		return self.url
	
	def __repr__(self):
		return "<urlinfo url='%s'>" % self.__str__()
	
	def __contains__(self, key):
		return key in self.__dict

	def __len__(self):
		return len(self.__dict)
		
	def __getitem__(self, key):
		return self.__dict[key]
	
	def __setitem__(self, key, value):
		self.__dict[key] = value
	
	def __delitem__ (self, key):
		del(self.__dict[key])
	
	
	
	
	# DISPLAY (for convenience in interpreter)
	def display(self):
		trix.display(self.__dict)
	
	# KEYS
	def keys(self):
		return self.__dict.keys()
	
	# ADDR INFO
	def addrinfo(self, **k):
		"""
		Use kwargs to narrow search to given family, type, protocol.
		
		EXAMPLE:
		ui = urlinfo("http://laptop.local")
		addr = ui.addrinfo(family="SOCK_STREAM")
		"""
		info=self.__dict
		host=port=family=stype=proto=flags=None
		try:
			dhost = k.get('defhost', self.__defhost)
			host = self.__dict.get('host', dhost)
			try:
				port = self.__dict['port']
			except:
				raise ValueError('err-addrinfo', xdata(
						reason='port-required', detail='specify-port'
					))
			
			#
			# Allow kwargs to be given as string, rather than integer 
			# values.
			#
			family = trix.value('socket', k.get('family')) or 0
			proto = trix.value('socket', k.get('proto')) or 0
			flags = trix.value('socket', k.get('flags')) or 0
			stype = trix.value('socket', 
					k.get('kind') or k.get('type') or k.get('socktype'), 
					default=0
				)
		
			# return address info list
			return socket.getaddrinfo(host,port,family,stype,proto,flags)
		except Exception as ex:
			raise type(ex)(ex.args, xdata(error='err-addrinfo-fail',
					host=host, port=port, family=family, stype=stype,
					proto=proto, flags=flags, info=self.__dict
				))
	
	
	
	
	@property
	def dict(self):
		"""Dict containing individual parsed values."""
		return self.__dict
	
	@property
	def url(self):
		"""URL string."""
		if self.scheme:
			scheme = self.scheme+'://'
		elif self.host:
			scheme = '//'
		else:
			scheme = ''
		
		return "%s%s%s%s%s%s%s%s%s" % (scheme, 
			self.username      if self.username else '',
			":****"            if (self.username and self.password) else '',
			"@"                if self.username else '',
			self.host          if self.host else '',
			":"+str(self.port) if self.port else '',
			self.path          if self.path else '',
			"?"+self.query     if self.query else '',
			"#"+self.fragment  if self.fragment else ''
		)
	
	@property
	def scheme(self):
		return self.__dict.get('scheme')
	
	@property
	def wrap(self):
		return self.__dict.get('wrap')
	
	@property
	def username(self):
		return self.__dict.get('username')
	
	@property
	def password(self):
		return self.__dict.get('password')
	
	@property
	def netloc(self):
		return self.__dict.get('netloc')
	
	@property
	def host(self):
		return self.__dict.get('host')
	
	@property
	def port(self):
		return self.__dict.get('port')
	
	@property
	def path(self):
		return self.__dict.get('path')
	
	@property
	def fragment(self):
		return self.__dict.get('fragment')
	
	@property
	def query(self):
		return self.__dict.get('query')
	
	@property
	def qdict(self):
		try:
			return self.__qdict
		except:
			self.__qdict = urlparse.parse_qs(self.query)
			return self.__qdict
	
	
	
	#
	# PARSE
	#
	def __parse(self):
		url, k = self.__params
		if 'port' in k:
			k['port'] = int(k['port'])
		
		# kwargs
		if not url:
			return self.__uparsedict({}, k)
		
		# dict
		try:
			url.update({})
			if 'port' in url:
				url['port'] = int(url['port'])
			return self.__uparsedict(url, k)
		except ValueError:
			raise
		except Exception:
			pass
		
		# int
		try:
			int(url) + 0
			return self.__uparsedict(dict(port=int(url)), k)
		except Exception as ex:
			pass
		
		# tuple
		try:
			return self.__uparsedict(dict(host=url[0], port=int(url[1])), k)
		except:
			pass
		
		raise Exception('url-parse-fail', xdata(reason='invalid-argument',
				url=url, k=k
			))
	
	
	#
	# PARSE-STRING
	#
	def __uparsestr(self):
		url, k = self.__params
		
		try:
			R = {}
			
			# get the meat of the url
			x = urlparse.urlparse(url)
			s,n,p,q,f = x.scheme, x.netloc, x.path, x.query, x.fragment
			
			# update with urlparse results
			R.update(dict(scheme=s, netloc=n, path=p, query=q, fragment=f))
			
			# separate host, port, user, and password from the netloc
			R.update(self.__authority(x.netloc))
			
			# defaults - update(k), check scheme/port and wrap
			try:
				self.__defaults(R, k)
			except Exception:
				raise Exception(xdata(R=R, k=k))
			
			# save result
			self.__dict = R
		except Exception:
			raise Exception(xdata())
	
	
	
	#
	# PARSE-DICT
	#
	def __uparsedict(self, urldict, k):
		# since all params are dict, simply pop the keys
		R = trix.kpop(urldict, self.__Keys)
		
		# apply defaults from k before self.__defaults
		R.update(k)
		
		# apply defaults and save dict
		self.__defaults(R, k)
		self.__dict = R
	
	
	
	#
	# AUTHORITY
	#
	def __authority (self, s):
		
		# Splits string in format of "username:password@host:port" and 
		# returns a dict containing those parts. The 'host' part is 
		# required. If included, the 'port' will be cast as an integer.
		if s:
			a = s.split('@')
			if len(a) == 2: # user:pass@host:port
				host,port = self.__authsplit(a[1])
				user,pswd = self.__authsplit(a[0])
			elif len(a) == 1: # host:port only
				host,port = self.__authsplit(a[0])
				user,pswd = (None,None)
			
			if not user:
				user = ''
			if not pswd:
				pswd = ''
			
			try:
				if port:
					port = int(port)
				return dict(host=host,port=port,username=user,password=pswd)
			except:
				pass
		return dict(host=None,port=None,username=None,password=None)
	
	
	
	#
	# AUTH-SPLIT
	#
	def __authsplit(self, s):
		
		# Split on ':' and return a tuple of at least two values, any of
		# which may be None.
		x = s.split(':')
		if x:
			return (x[0],None) if len(x)==1 else tuple(x)
		return (None,None)
	
	
	
	#
	# DEFAULTS
	#
	def __defaults(self, R, k):
		
		# apply defaults specified by k before continuing
		R.update(k)
			
		# fill in port/scheme if one is empty
		port = int(R.get('port', 0) or 0)
		schm = R.get('scheme')
		if schm and not port: 
			try:
				R['port'] = socket.getservbyname(schm)
			except:
				pass
		elif port and not schm: 
			try:
				R['scheme'] = socket.getservbyport(port)
			except:
				pass
		
		# sanitize
		for k in R:
			if R[k] == None:
				R[k] = b''
		
		#
		# default-host
		#  - this is usually ok to leave '', but I guess not always
		#
		if not R.get('host'):
			R['host'] = self.__defhost
		
		# check for schemes/ports that should be wrapped for ssl
		wrap = (schm in WRAP_SCHEMES) or (port in WRAP_PORTS)
		R.setdefault('wrap', wrap)



#
# SSL WRAPPER SCHEMES/PORTS
#  - There are surely lots more of these out there, both for port and
#    for scheme. These are the ones I've found so far. I'll add more 
#    as I encounter them.
#

WRAP_SCHEMES = [
	'nsiiops', 'https', 'smtps', 'nntps', 'sshell', 'ldaps', 
	'ftps-data', 'ftps', 'telnets', 'imaps', 'ircs', 'pop3s', 
	'ircs'
]

WRAP_PORTS = [
	6697 # common ircs port
]
	

