#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ._sockurl import * # sockconf, sockurl
from .sockwrap import * # 
import select


DEF_HOST = '127.0.0.1'


class sockcon(sockurl, sockwrap):
	"""Socket connection class implements i/o methods."""
	
	def __init__(self, config=None, **k):
		"""
		Pass socket connection params, buflen (int), and optional 
		encoding and errors parameters.
		
		Accepts kwargs 'family', 'proto', and 'kind' (with aliases 'type'
		and 'socktype' being equal to 'kind'), which act as a filter for
		possible values as determined by urlinfo's `addrinfo` results.
		
		The 'ctimeout' value may also be specified by kwarg to override
		the default or value given to the constructor.
		"""
		
		# init config
		sockurl.__init__(self, config, **k)
		
		# make sure connection has a host
		if not self.config.get('host'):
			self.config['host'] = DEF_HOST
			self.url['host'] = DEF_HOST
		
		#
		# CREATE THE CONNECTION SOCKET/PASS DIRECTLY TO SOCK-WRAP
		#  - The sockwrap class accepts a true socket object, not a proxy.
		#    Subclasses *may* create the socket, but MUST NOT STORE IT.
		#    In such a case the original socket object must be passed here
		#    immediately but NOT stored internally.
		#  - This is very important; Losing track of a socket object may
		#    cause the socket to stay active (and its port unusable) after
		#    the program exits.
		#
		#    REMEMBER...
		#  - DO NOT STORE the actual socket object anywhere but sockprop.
		#
		sockwrap.__init__(self, self.__connect(), self.config)

	
	@property
	def buflen(self):
		"""Return the configured buffer length."""
		try:
			return self.__buflen
		except:
			self.__buflen = self.config.get('buflen', DEF_BUFFER)
			return self.__buflen
	
	
	# CONNECT
	def __connect(self, **k):
		#
		# REMEMBER...
		#  - DO NOT STORE the actual socket object anywhere but sockprop!
		#
		
		# setup...
		ctimeout = self.config.get('ctimeout', SOCK_CTIMEOUT)
		
		try:
			aainfo = self.url.addrinfo(**k)
		except socket.gaierror as ex:
			raise type(ex)(ex.args, xdata(error="err-connect-fail",
					config=self.config, url=self.url, k=k
				))
		
		#
		# Loop through possible addresses trying each until a successful
		# connection is made.
		#
		s = None
		ok = False
		errs = []
		starttm = time.time()
		for ainfo in aainfo:
			i = 0
			try:
				s = socket.socket(ainfo[0], ainfo[1], ainfo[2])
				if self.config.get('wrap'):
					s = trix.module('ssl').wrap_socket(s)
				s.settimeout(ctimeout)
				s.connect(ainfo[4])
				
				#
				# RETURN SOCKET OBJECT
				#  - This method is private so that only the constructor may
				#    call for a socket.
				#  - The socket must not be stored here, or anywhere except
				#    the `sockprop` class (by way of `sockwrap`, which also
				#    does NOT store the object directly!)
				#
				return s
			
			except Exception as ex:
				errs.append(
						dict(xtype=type(ex), a=ex.args, ainfo=ainfo
					)) 
		
		raise Exception("err-connect-fail", xdata(
			aainfod=[cls.__ainformat(a) for a in aainfo], 
			starttm=starttm, endtime=time.time(), ctimeout=ctimeout,
			uidict=self.url.dict, a=(self.config), socket=repr(s), 
			errs=errs
		))
		
		
	
	
	@classmethod
	def __ainformat(self, ainfo):
		#
		# Utility for reporting errors that may occur in `__connect`.
		#
		return {
			"family" : ",".join(sockname(ainfo[0], "AF_")),
			"kind"   : ",".join(sockname(ainfo[1], "SOCK_")),
			"proto"  : ainfo[2],
			"cannon" : ainfo[3],
			"addr"   : ainfo[4]
		}


