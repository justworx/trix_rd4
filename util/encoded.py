#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .stream.buffer import *
from . import bom, enchelp


class Encoded(object):
	"""Represents raw byte strings."""
	
	EncodingKeywords = [b'charset',b'encoding',b'coding']
	
	def __init__(self, bbytes):
		"""Pass encoded byte strings."""
		self.__buffer = Buffer(bbytes)
		self.__ekw = self.EncodingKeywords
	
	# 
	def reader(self):
		"""Returns a reader starting at seek(0)."""
		try:
			return self.__reader
		except:
			bpath = 'util.stream.buffer.Buffer'
			self.__buffer = trix.ncreate(bpath, self.bytes)
			self.__reader = self.__buffer.reader()
			self.__reader.seek(0)
			return self.__reader
	
	
	# NEW
	def decode(self, encoding, **k):
		"""Encoding argument required. Errors kwarg optional."""
		k['encoding'] = encoding
		k['mode'] = 'r'
		return self.__buffer.reader(**k).read()

	
	
	
	@property
	def bytes(self):
		return self.__buffer.read()
	
	
	@classmethod
	def pythonize(cls, enc):
		"""
		Use EncodingHelper validation to find a matching encoding name.
		If that fails, return the 
		"""
		try:
			enc = enc.decode('utf_8')
		except:
			print ('\n#\n# enc: %s\n#\n' % (enc))
			raise
			
		return enchelp.EncodingHelper(encoding=enc).encoding
	
	
	# DETECT
	def detect(self):
		"""
		Attempts to detect a valid encoding for bytes based either on BOM, 
		or the 'charset' or 'encoding' specification in the text,
		"""
		"""
		Attempts to detect encoding of raw bytes strings. This is not a
		comprehensive detection system - it provides an accurate encoding
		only for byte strings with a recognizable byte-order mark, or a
		likely encoding based on specification strings in the content of 
		the byte string.
		
		The detect() method works by first looking for a BOM and then, if
		that fails, looking for a specification in the text itself (in the
		form of encoding=<enc>, coding=<enc>, or charset=<enc>). 
		
		NOTES:
		 * The testbom() method WILL NOT WORK unless your bytestring
			 actually has a BOM at the head of it. This is pretty useful for
			 downloaded files, but most file system files neither start with
			 a BOM nor specify an encoding in the text (and even those that
			 do specify an encoding in the text may not be covered here!)
		 * The testspec() function totally relies on text files to specify
			 an encoding in the text file. Eg, <!SOMETAG charset=utf-8>. If
			 no such specification exists, testspec() is useless.
		 * Modern HTML files usually specify an encoding, but HTML coders
			 sometimes fail to get it right. I've seen plenty of charset
			 attributes that are misspelled or don't match any real encoding 
			 name.
		"""
		
		# Give it a try... testbom() is very fast, but only
		# catches a few encodings.
		e1 = self.testbom()
		if e1:
			return e1
		
		# Look for specification from the text. This is relatively fast
		# when it works, but could cause Exceptions. Just ignore them
		# and move on.
		try:
			return self.testspec()
		except:
			e2 = None
		
		# Hopefully one of them worked.
		e = e1 or e2
		
		#
		# DECODE THE ENCODING STRING!
		#  - Python3 requires encoding strings to be unicode. 
		#  - Python2 accepts it either way...
		#  - So... DO THIS! Decode the encoding string.
		#
		try:
			return e.decode('utf_8')
		except:
			return e
	
	
	#
	# Encoding Detection (weak).
	#
	
	# TEST BOM
	def testbom(self):
		return bom.testbom(self.bytes)
	
	# TEST SPEC
	def testspec(self):
		"""
		Test for the specification of an encoding in the form of:
		 * charset = "<encoding>"
		 * encoding = "<encoding>"
		 * coding = "<encoding>"
		
		Whitespace, assignment operators, and literal delimiters
		are optional.
		"""
		zero    = b"\0"
		blank   = b''
		ignore  = b'\t :=\'"'
		
		# dump multi-byte zero-padding of ascii characters
		bb = self.bytes.replace(zero, blank)
		
		# look for charset, coding (or encoding)
		for kw in self.__ekw:
			
			x = bb.find(kw) # start at the keyword kw
			if not x < 0:          
				p = x+len(kw) # pass the keyword               
				while bb[p] in ignore: # loop past whitespace
					p = p + 1
				
				r = [] # collect valid characters (to the next ignore char)
				while not bb[p] in ignore:
					r.append(bb[p])
					p = p + 1
				
				# this is the encoding value first specified in the text
				return self.pythonize(bytes(r))
	
	
	# TEST LIST
	def testlist (self, encodings=None):
		"""
		Attempts to decode then reencode byte string argument for each
		known encoding; Returns a list of encodings that succeed in this.
		Set the encodings argument as a list to limit encodings tested; 
		Default is ENCODINGS, which lists all documented encodings.
		
		Use this when searching manually for encodings that might work.
		It's definitely NOT a valid way to *automatically* detect an 
		encoding for actual use.
		
		Variety helps narrow the list, so pass the entire byte string.
		Check each matching encoding visually to see which gives correct 
		results.
		"""
		r = []
		for e in encodings or ENCODINGS:
			try:
				uu = self.bytes.decode(e)
				bb = uu.encode(e)
				if bb == self.bytes:
					r.append(e)
			except UnicodeError:
				pass
		return r


