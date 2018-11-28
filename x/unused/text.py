#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .enchelp import *


class Text(EncodingHelper):
	"""Represents text. Stores a unicode string and encoding params."""
	
	def __init__(self, text, **k):
		"""Pass text or bytes and encoding-related params."""
		EncodingHelper.__init__(self, **k)
		self.__set(text)
	
	def __str__(self):
		return self.__text
	
	def __bytes__(self):
		return self.bytes
	
	@property
	def text (self):
		"""The unicode text string object."""
		return self.__text
	
	@property
	def bytes (self):
		"""Returns bytes encoded using self.encoding."""
		try:
			return self.__bytes
		except:
			self.__bytes = self.text.encode(**self.ek)
			return self.__bytes
			
	
	# ENCODE
	def encode(self, encoding=None, errors=None):
		"""Encodes this text as bytes, applying any kwargs."""
		k = dict(encoding=encoding, errors=errors)
		return self.text.encode(**self.applyEncoding(k))
	
	
	#
	# SET TEXT
	#
	def __set(self, x):
		
		# set text to None
		self.__text = None
		
		#
		# Now try to calculate what self.__text should be.
		#
		if isinstance(x, unicode):
			#
			# UNICODE
			#  - It's unicode text, so just store the encoding (for use by
			#  - the bytes property) and store the unicode text.
			#
			self.__text = x
		
		
		else:
			
			#
			# BYTES
			#  - set bytes property (since we already have the value)
			#  - try to detect encoding (if not provided to constructor)
			#  - try to convert bytes to unicode
			#
			self.__bytes = x
			
			#
			# ENCODING SPECIFIED
			#  - if an encoding was provided to the constructor, use it to
			#    decode the bytes.
			#  - Since the encoding was specified, don't allow any leniency
			#    but throw an exception if `decode()` fails.
			#
			if self.ek:
				self.__text = x.decode(**self.ek)
				return
			
			#
			# NO ENCODING
			#  - no encoding was specified, so try to detect.
			#  - if detection fails, just try DEF_ENCODEt
			#  - if that fails, try to decode it with no args
			#  - otherwise, raise an error.
			#
			else:
				# Try to detect encoding.
				eb = trix.ncreate("util.encoded.Encoded", x)
				de = eb.detect()
				
				if de:
					try:
						# Try decoding with detected encoding.
						self.__text = eb.bytes.decode(de)
						return
					except:
						pass
				
				try:
					#
					# If that failed (eg., due to mislabling of encoding),
					# try decoding with DEF_ENCODE.
					#
					self.__text = eb.bytes.decode(DEF_ENCODE)
					return
				except:
					pass
				
				try:
					#
					# If all of the above fails, try casting the bytes as
					# unicode.
					#
					self.__text = unicode(eb.bytes)
					return
				except:
					pass
				
				
				#
				# If the given bytes could not be converted to unicode, raise
				# an exception here.
				#
				raise ValueError('encoding-required',  xdata(
						paramset1=['unicode', 'bytes+encoding'], 
						x=x, ek=self.ek
					))


