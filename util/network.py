#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import *
import socket
try:
	import queue
except:
	import Queue as queue



class Host(object):
	"""Network information."""
	
	def __init__(self, host=None):
		
		# host, fqdn
		self.__host = host or socket.gethostname()
		self.__fqdn = socket.getfqdn(self.__host)
		self.__dbg = []
		
		# hostx
		try:
			self.__hostx = socket.gethostbyname_ex(self.__host)
			self.__name = self.__hostx[0]
			self.__alias = self.__hostx[1]
			self.__addrs = self.__hostx[2]
		except Exception as ex:
			self.__dbg.append(dict(hostx=["err", type(ex), ex.args]))
			self.__hostx = None
			self.__name = None
			self.__alias = None
			self.__addrs = None
		
		# get ip address
		try:
			self.__ip = self.__hostx[2]
		except Exception as ex:
			self.__ip = ''
		
		# split hostname by dots (eg, laptop.local, www.somesuch.com)
		try:
			self.__parts = self.hostx[2].split('.')
		except Exception as ex:
			self.__parts = []
		
		# check parts
		check = []
		try:
			selflocal = "%s.local" % self.__host
			self.__local = socket.gethostbyname_ex(selflocal)
		except Exception as ex:
			self.__local = None
	
	
	# STATUS
	def status(self):
		return dict(
			ip = self.ip,
			six = self.six,
			fqdn = self.fqdn,
			host = self.host,
			name = self.name,
			hostx = str(self.hostx),
			parts = str(self.parts),
			local = str(self.__local)
		)
	
	
	# DISPLAY
	def display(self, **k):
		trix.display(self.status(), **k)
	
	
	# PORT-SCAN
	def portscan(self):
		"""
		Pass an integer representing the highest port to scan, two ints
		representing the range of ports to scan (lowest first, then high),
		or pass nothing to scan the full range of ports (1-65536).
		"""
		r = []
		for port in range(0, 2**16):
			try:
				s = socket.socket()
				s.connect((self.host, port))
				r.append(port)
			except (OSError, socket.error) as ex:
				pass
			except Exception as ex:
				raise
		return r

	@property
	def six(self):
		"""True if ipv6 is available, else False."""
		return socket.has_ipv6
	
	@property
	def ip(self):
		return self.__ip
		
	@property
	def parts(self):
		return self.__parts
		
	@property
	def host(self):
		return self.__host
		
	@property
	def fqdn(self):
		return self.__fqdn
	
	@property
	def hostx(self):
		return self.__hostx
	
	@property
	def local(self):
		return self.__local
	
	@property
	def name(self):
		return self.__name
	
	@property
	def alias(self):
		return self.__alias
	
	@property
	def addrs(self):
		return self.__addrs
