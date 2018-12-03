#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#


#
# HTTP (REQUEST PARSER)
#
class httpreq(object):
	"""Simple HTTP request parser."""
	
	def __init__(self, requestBytes):
		"""Receives requestBytes; loads properties with values."""
		self.__bytes = requestBytes
		self.__text = requestBytes.decode('utf_8')
		
		# array of request lines
		self.__lines = L = self.__text.splitlines()
		
		# request info
		self.__request = L[0]
		self.__reqinfo = L[0].split()
		
		# request properties
		self.__method = self.reqinfo[0]
		self.__version = self.reqinfo[2]
		self.__reqpath = self.reqinfo[1]
		if self.__reqpath and len(self.__reqpath):
			self.__reqpath = self.reqpath[1:]
		
		# produce a dict of {keys : values}
		self.__headers = H = {}
		for l in L[1:]:
			if not l:
				break
			sp = l.split(":", 1)
			hk = sp[0].strip()
			try:
				H[hk] = sp[1].strip()
			except:
				H[hk] = ''
	
	@property
	def bytes(self):
		return self.__bytes	
	
	@property
	def text(self):
		return self.__text	
	
	@property
	def lines(self):
		return self.__lines	
	
	@property
	def request(self):
		return self.__request	
	
	@property
	def reqinfo(self):
		return self.__reqinfo	
	
	@property
	def method(self):
		return self.__method	
	
	@property
	def version(self):
		return self.__version	
	
	@property
	def reqpath(self):
		return self.__reqpath	
	
	@property
	def headers(self):
		return self.__headers	
	
