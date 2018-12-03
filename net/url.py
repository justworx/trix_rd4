#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.enchelp import * # trix

# Compensate for renamed symbols in python 3:
#  - MessageMerge is MM2 in python2, MM3 in python3.
#  - Never use MM2 or MM3 directly - use MessageMerge so it will work
#    in both 2 and 3.

class MM2(object):
	"""
	def contentenc
	"""
	@classmethod
	def contentenc(cls, i): return i.getencoding();
	@classmethod
	def contenttype(cls, i): return i.gettype();
	@classmethod
	def maintype(cls, i): return i.getmaintype();
	@classmethod
	def subtype(cls, i): return i.getsubtype();
	@classmethod
	def param(cls, i, pname): return i.get(pname)#.getparam(pname)

class MM3(object):
	@classmethod
	def contentenc(cls, i): return i.get_encoding();
	@classmethod
	def contenttype(cls, i): return i.get_content_type(); 
	@classmethod
	def maintype(cls, i): return i.get_content_maintype();
	@classmethod
	def subtype(cls, i): return i.get_content_subtype();
	@classmethod
	def param(cls, i, pname): return i.get_param(pname)


#  - urlreq is 'urllib2' in python2, urllib.request in python3

try:
	from urllib.request import Request, urlopen  # Python 3
	MessageMerge = MM3
except ImportError:
	from urllib2 import Request, urlopen  # Python 2
	MessageMerge = MM2



def parse(url, **k):
	"""Parse url and return urlinfo object."""
	try:
		return trix.ncreate('util.urlinfo.urlinfo', url, **k)
	except:
		from . import urlinfo
		return urlinfo.urlinfo(url, **k)


#
# FUNCTIONS
#

def open(url, *a, **k):
	"""
	Returns a UResponse object for the given url. Arguments are the 
	same as for urllib's urlopen() function.
	
	from net import url
	r = url.open(someUrl)
	"""
	return UResponse(url, *a, **k)


def head(url):
	"""
	Returns a UResponse with just the head for the given url.
	
	from net import url
	h = url.head(someUrl)
	print (h.info())
	"""
	request = Request(url)
	request.get_method = lambda : 'HEAD'
	return UResponse(request)



#
# URL - DOWNLOAD
#

class UResponse(object):
	"""Response object for the url.open() function."""
	
	MxEncSeek = 16384
	
	def __init__(self, *a, **k):
		"""Arguments are the same as for urllib.urlopen()"""
		
		#
		# open the file
		#
		q = Request(*a)
		if k:
			for header in k:
				q.add_header(header, k[header])
		
		self.__file = urlopen(q)
		self.__info = self.__file.info()
		
		# buffer type
		TBuffer = trix.nvalue('util.stream.buffer.Buffer')
		
		# buffer... reads bytes
		content = self.__file.read()
		
		# decompress (if gzip)
		hh = self.__info
		try:
			if hh['Content-Encoding'] in ['gzip']:
				import zlib
				content = zlib.decompress(content, 16+zlib.MAX_WBITS)
		except:
			raise Exception("gzip decompression", xdata(info=dict(hh), 
					content=content)
				)
			
		self.__buf = TBuffer(content)
		self.__buf.seek(0)
		
		#
		# Find the encoding, if possible;
		#  - hopefully the charset is in the headers
		#
		c = self.param('charset')
		if not c:
			
			#
			# If no charset in params, lock the thread (so no other thread
			# can manipulate the buffer... not likely, but possible).
			#
			with thread.allocate_lock():
				
				# just read a few bytes for testbom
				self.__buf.seek(0)
				c = trix.ncreate(
					"util.bom.testbom", self.__buf.reader().read(16)
				)
				
				# At this point, the reader can only do bytes; we need to use
				# it to find the encoding.
				if not c:
					sz = self.MxEncSeek
					self.__buf.seek(0) # start over; read max 16k
					bb = trix.ncreate(
							'util.encoded.Encoded', self.__buf.reader().read(sz)
						)
					c = bb.detect() # look for encoding specifier in file
		
		# now set self.__charset, even if it's None
		self.__charset = c
		
		#
		# If an encoding was found, create a new Buffer object complete
		# with encoding, then read the bytes into it.
		#
		if self.__charset:
			self.__buf.seek(0)
			self.__buf = TBuffer(self.__buf.read(encoding=self.__charset))
			self.__buf.seek(0)
	
	
	@property
	def contenttype(self):
		"""The content type, as given by 'info'."""
		return MessageMerge.contenttype(self.info())
	
	@property
	def contentenc(self):
		"""..."""
		return MessageMerge.contentenc(self.info())
	
	@property
	def maintype(self):
		"""The main type, as given by 'info'."""
		return MessageMerge.maintype(self.info())
	
	@property
	def subtype(self):
		"""The sub-type, as given by 'info'."""
		return MessageMerge.subtype(self.info())
	
	@property
	def charset(self):
		"""Return the document's encoding."""
		return self.__charset
		
	
	
	# READER
	def reader(self, **k):
		"""Return a reader from the internal buffer."""
		if self.__charset:
			k.setdefault('encoding', self.__charset)
		return self.__buf.reader(**k)
	
	# DISPLAY
	def display(self):
		"""Print r.info()"""
		print (str(self.info()))
	
	
	# GET URL
	def geturl(self):
		"""The actual URL of the resource retrieved."""
		return self.__file.geturl()
	
	# GET CODE
	def getcode(self):
		"""Response code."""
		return self.__file.getcode()
	
	# INFO
	def info(self):
		"""Message objects, as returned by python's urlopen()."""
		try:
			return self.__info
		except:
			self.__info = self.__file.info()
			return self.__info
	
	# PARAM
	def param(self, name):
		"""Param, as from the info Message object."""
		return MessageMerge.param(self.info(), name)


