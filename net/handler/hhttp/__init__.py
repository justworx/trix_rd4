#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from time import gmtime, strftime
from ....util import urlinfo, mime
from ....net.handler import *
from ....net.httpreq import *


#
# HANDLE-HTTP
#
class HandleHttp(Handler):
	"""
	Replies with the default HTTP content handler - a message about 
	this class and how to customize it to suit your needs.
	"""
	
	WebContent = "net/handler/hhttp/example/"
	
	# INIT
	def __init__(self, sock, **k):
		
		# make root dir configurable
		self.rootdir = k.get('rootdir')
		
		# set default path to the example content files (if necessary)
		if not self.rootdir:
			self.rootdir = trix.innerfpath(self.WebContent)
		
		Handler.__init__(self, sock, **k)
		
		# webroot is an fs.Path object
		self.webroot = trix.path(self.rootdir)
		
		# configurable header items
		self.Server = k.get("Server", "trix/%s" % str(VERSION))
		self.Connection = k.get("Connection", "keep-alive")
	
	
	
	#
	# HANDLE DATA
	#
	def handledata(self, data, **k):
		"""
		Received a request; process and return reply.
		"""
		try:
			#1 Parse Headers
			self.request = httpreq(data)
			
			#2 Parse URL
			self.uinfo = urlinfo.urlinfo(self.request.reqpath)
			self.uquery = self.uinfo.query
			
			# full path string to requested document
			reqpath = self.webroot.merge(self.uinfo.path)
			
			# and a path object
			self.reqpath = trix.path(reqpath)
			
			# apply default file (index.html)
			if self.reqpath.isdir():
				reqpath = self.reqpath.merge('index.html')
			
			#4 Check mime type
			self.contentType = mime.Mime(reqpath).mimetype
			
			#5 Load File Content
			content = trix.path(reqpath).reader(encoding="utf_8").read()
			
			#6 Generate Headers
			clength = len(content.encode('utf_8'))
			
			#7 Write the response header and
			gmt = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
			head = self.head('200', clength)
			
			#8 Send End Bytes
			self.write(head + "\r\n\r\n" + content + "\r\n\r\n")
			
		except BaseException as ex:
			#print (ex, xdata())
			self.writeError("500", xdata())
			raise
	
	
	#
	# HEAD - Generate head text.
	#
	def head(self, result, clength):
		"""Return the head for the response."""
		gmt = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
		head = "\r\n".join([
			"HTTP/1.1 %s OK"     % result, 
			"Date: %s"           % (gmt),
			"Connection: %s"     % (self.Connection),
			"Server: %s"         % (self.Server),
			"Accept-Ranges: bytes",
			"Content-Type: %s"   % self.contentType,
			"Content-Length: %i" % (clength),
			"Last-Modified: %s"  % (gmt) # this should be the file mod date
		])
		return head
	
	
	#
	# WRITE-ERROR - Writes error page to client.
	#
	def writeError(self, errcode, xdata=None):
		"""
		Write an error response given `errcode` and optional `xdata`.
		"""
		try:
			b = trix.ncreate('util.stream.buffer.Buffer', encoding='utf_8')
			w = b.writer()
			
			w.write("<html><head>\r\n")
			w.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\r\n')
			w.write("<title>Error</title>\r\n")
			w.write("</head><body>\r\n")
			
			if errcode == '404':
				w.write("<h1>404 File Not Found Error</h1>\r\n")
			else:
				w.write("<h1>500 Internal Server Error</h1>\r\n")
			w.write("<pre>\r\n")			
			
			if xdata:
				# gotta make entities out of gt & lt...
				xdatae = trix.formatter(f='JDisplay').format(xdata)
				xdatae = xdatae.replace(">", "&gt;")
				xdatae = xdatae.replace("<", "&lt;")
				#print (xdatae)
				w.write(xdatae)
			w.write("</pre>\r\n</body></html>\r\n\r\n")
			
			# SEND the error page.
			head = self.head(errcode, w.tell())
			self.write("%s\r\n\r\n" % (head.encode('utf_8')))
			
			# read the response from the Buffer, b
			self.write(b.read())
		
		except Exception as ex:
			pass
			# debug message
			#print ("\n\n\n\n\nERROR HANDLING EXCEPTION!\n\n\n\n", str(ex))
			#raise

