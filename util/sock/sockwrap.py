#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from ._sockconf import *
from ..enchelp import *
from ._sockprop import *
from ... import * # trix
import socket, select


class SockError(OSError): pass
class SockFatal(SockError): pass


#
# I'm open to suggestions on these values. They work well for me, but
# I don't really know how to guess the best values for general use.
#
DEF_BUFFER = 4096       
DEF_LINEEND = "\r\n"


class sockwrap(sockconf, EncodingHelper, sockprop):
	"""Socket connection class implements i/o methods."""
	
	def __init__(self, sock, config=None, **k):
		"""
		Pass socket and optional kwargs buflen, newl, encoding/errors.
		"""
		try:
			#
			# DO NOT INIT SOCKCONF HERE! (YET)
			#  - Try to just update self.config with defaults needed by 
			#    sockwrap. The sockwrap class might play superclass to 
			#    others, so don't destroy self.config if it already exists!
			#  - YET... if config isn't something that can be updated, go
			#    ahead and initialize sockconf in the except clause.
			#
			if config:
				self.config.update(config)
			self.config.update(k)
			
		except AttributeError:
			#
			# DO INIT SOCKCONF! SOCKWRAP IS *NOT* SUPERCLASS
			#  - If there's an AttributeError, it means config has not yet 
			#    been defined, so call sockconf.__init__ here.
			#
			sockconf.__init__(self, config, **k)
		
		#
		# REGARDLESS OF THE ABOVE...
		#  - Init these values with defaults and call EncodingHelper and
		#    sockprop constructors.
		#
		
		#
		# These are definitely needed by all connecting sockets (and will
		# be ignored by server sockets).
		#
		self.__buflen = self.config.get('buflen', DEF_BUFFER)
		self.__newl = self.config.get('newl', DEF_LINEEND)
		
		# init encoding
		k.setdefault('encoding', DEF_ENCODE)
		EncodingHelper.__init__(self, config, **k)
		
		
		#
		# STORING THE SOCKET
		#  - The sockwrap class accepts a true socket object, not a proxy.
		#    Subclasses *may* create the socket, but MUST NOT STORE IT.
		#    In such a case the original socket object must be passed here
		#    immediately but NOT stored internally.
		#  - From here, pass the socket object directly to sockprop, which
		#    will store the only copy of the exact socket object reference
		#    securely and will share a proxy to the socket via its socket
		#    property. This will - hopefully - prevent the socket from
		#    remaining in memory after the program exits.
		#
		#    AGAIN...
		#  - DO NOT STORE the actual socket object anywhere but sockprop.
		#
		sockprop.__init__(self, sock)
	
	
	@property
	def buflen(self):
		"""Buffer length, as given to init. Default: DEF_BUFFER (4096)"""
		return self.__buflen
	
	@property
	def newl(self):
		"""New-line character set; Eg, '\n', '\r', '\r\n'."""
		return self.__newl
	
	
	
	# WRITE
	def write(self, text, **k):
		"""
		Encode text to bytes (by encoding specified to constructor) and 
		send. Default encoding is trix.DEF_ENCODE.
		"""
		return self.send(text.encode(**self.extractEncoding(k)))
	
	# WRITELINE
	def writeline(self, text, **k):
		"""Write text, appending `self.newl` line ending."""
		self.write("%s%s" % (text, self.newl), **k)
	
	# READ
	def read (self, sz=None, **k):
		"""Decode received data and return it as text."""
		try:
			bdata = self.recv(sz or self.buflen)
		except socket.timeout:
			return ''
		
		if bdata:
			try:
				return bdata.decode(**self.ek)
			except UnicodeDecodeError as ex:
				raise SockError("err-read-fail", xdata(
						reason = "unicode-decode-error",
						oxtype = str(type(ex)), 
						fmtdate = time.strftime("%Y-%m-%d %H:%M:%S"),
						bytedata = bdata, python=str(ex)
					))
	
	
	#
	# SEND
	#
	def send(self, data):
		"""
		Send `data` bytes.
		
		ERRORS (and how to handle them):
		 * socket.timeout : In the event of socket.timeout errors, retry
		   sending until you succeed or are ready to give up.
		 * socket.error : On socket.error exceptions, the socket is 
		   shutdown, so you have to reconnect and renegotiate the
		   transmition in whatever way is appropriate to your situation.
		 * For other exception types check the `python` xdata key for
		   clues to help debug the problem.
		"""
		try:
			if not self.socket:
				raise SockFatal('err-send-fail', xdata(
						detail='send-error', reason='socket-closed',
						config=self.config
					))
			
			if data:
				try:
					return self.socket.send(data)
				except (socket.timeout, socket.error) as ex:
					raise SockError('err-send-fail', xdata(
						reason='send-error', python=str(ex)
					))
				except Exception as ex:
					raise SockError('err-send-fail', xdata(
						reason='send-error', python=str(ex)
					))
		
		except ReferenceError:
			#
			# The socket has shutdown and been deleted. Don't whack out any
			# __del__ methods with a ReferenceError... just ignore this.
			#
			pass
	
	
	#
	# RECV
	#
	def recv(self, buflen):
		"""
		Return any received data, or None if no data has been received.
		"""
		if not self.socket:
			raise SockFatal(xdata(error='err-recv-fail', 
					detail="sock-receive-err", reason='socket-closed',	
					config=self.config
				))
		
		s = self.socket
		if s:
			
			#
			# Get next buffer of received data. If none arrives before
			# timeout, then return an empty string ''.
			#
			try:
				try:
					# POLL - DON'T WAIT FOR TIMEOUT
					R,W,X = select.select([s],[],[s],0)
				except Exception as ex:
					# If this system doesn't support select.select(), convert
					# to using self.socket.recv directly (for future calls).
					self.recv = self.socket.recv
				
				# receive
				if R:
					return s.recv(buflen)
				if X:
					raise SIOError(x)
			
			# timeout - return empty string.
			except socket.timeout:
				return ''
			
			#
			# If there's an actual error, repackage it as either SockError
			# or SockFatal.
			#
			except socket.error as ex:
				
				# default error data
				error = 'err-recv-fail'
				errno = None
				errstr = ''
				xreason = ''
				xfatal = False
				
				# package error data
				try:
					if isinstance(ex, basestring):
						errstr = ex
					else:
						xfatal = True
						errno = ex[0]
						if errno == 10058:
							errstr = "Recv attempt after peer disconnect."
							xreason = 'recv-after-disconnect'
						elif errno == 10054:
							errstr = "Peer brutishly disconnected. (Server)"
							xreason = 'peer-brutishly-disconnected'
							#xdetail = 'whatever-that-means'
						elif errno == 10053:
							errstr = "Connection forcibly closed by remote host."
							xreason = 'host-closed-connection'
						else:
							xfatal = False
				except:
					pass
				
				#
				# Apparently converting `ex` string can cause an exception,
				# so we need to be careful not to lose any valid info here.
				#
				try:
					EX = str(ex)
				except:
					EX = ""
				
				ARGS = [ex.args, xdata(
						error=error, errno=errno, errstr=errstr, xreason=xreason, 
						xtype=str(type(ex)), config=self.config, EX=EX
					)
				]
				
				if xfatal:
					raise SockFatal(*ARGS)
				else:
					raise SockError(*ARGS)
