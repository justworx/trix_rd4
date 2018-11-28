#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *
import encodings.aliases


class EncodingHelper(object):
	"""Holds default encoding and (optionally) errors."""
	
	__EE = ['encoding', 'errors']
	Strict = False
	
	def __init__(self, config=None, **k):
		"""Pass default encoding and (optionally) errors kwargs."""
		
		config = config or {}
		config.update(k)
		
		self.__ek = {}
		self.__given = enc = config.get('encoding')
		self.__strict = config.get('strict', self.Strict)
		
		# Make sure encoding and errors were given as unicode; any error
		# still brings the correct result. (I think. I hope.)
		enc = config.get('encoding')
		err = config.get('errors')
		
		try:
			enc = enc.decode()
			err = err.decode()
		except AttributeError:
			pass
		
		# Make sure `enc` matches (or is alias to) a valid encoding 
		# defined in encodings.aliases.
		enc = self.validate(enc)
		
		# store the encoding and errors values
		if enc:
			self.__ek['encoding'] = enc
			err = config.get('errors')
			if err:
				self.__ek['errors'] = err
		
	@property
	def ek(self):
		"""
		Return dict with default 'encoding' and 'errors' values as given
		to this object's constructor.
		"""
		return self.__ek
	
	@property
	def encoding(self):
		"""Default encoding."""
		return self.__ek.get('encoding')
	
	@property
	def errors(self):
		"""Default errors value."""
		return self.__ek.get('errors')
	
	@property
	def strict(self):
		"""Given encodings must match a python encoding or alias."""
		return self.__strict
	
	
	
	# EXTRACT
	def extractEncoding(self, k):
		"""
		Remove and return encoding and errors from dict `k`, with results
		from self.ek as defaults.
		
		 * take the 'encoding' and 'errors' out of k
		 * apply default 'encoding' and 'errors' from self.ek
		 * validate dict to make sure 'errors' doesn't exist without an
		   'encoding' or if encoding is None.
		 * return a dict blank, with encoding, or with encoding and errors
		"""
		r = {}
		
		# take the encoding and errors out of k...
		ee = trix.kpop(k, 'encoding errors')
		
		# calculate the return values
		enc = ee.get('encoding', self.encoding)
		if enc:
			err = ee.get('errors', self.errors)
			if err:
				return dict(encoding=enc, errors=err)
			else:
				return dict(encoding=enc)
		return {}
		
	
	# APPLY
	def applyEncoding(self, k):
		"""
		Apply self.ek params to dict `k` as defaults. If None is passed
		for either value, that value will be excluded from the results.
		If encoding is removed, errors must be removed, too.
		
		Returns the given `k`, updated with any alterations.
		"""
		r = {}
		
		# If encoding is specifically None, remove encoding and errors
		# from k, then return k.
		if ('encoding' in k) and (k['encoding']==None):
			trix.kpop(k, 'encoding errors')
			return k
		
		# Otherwise, manipulate values as appropriate.
		if ('encoding' in k) and k['encoding']:
			r['encoding'] = k['encoding']
		elif self.encoding:
			r['encoding'] = self.encoding
		
		if 'encoding' in r:
			if ('errors' in k) and k['errors']:
				r['errors'] = k['errors']
			elif self.errors:
				r['errors'] = self.errors
		
		# Finally, return `k` in its altered state.
		trix.kpop(k, 'encoding errors')
		k.update(r)
		return k
	
	
	# SANS
	def sansEncoding(self, k):
		"""Return all keys from `k` except 'encoding' and 'errors'."""
		r = {}
		for key in k:
			if key not in self.__EE:
				r[key] = k[key]
		return r
	
	
	@classmethod
	def altalias(cls, enc):
		"""Return a matches without underscore, dash, or dots."""
		enc = enc.replace('_','').replace('.','').lower()
		
		# find aliase in ENCODINGS list
		for val in ENCODINGS:
			val = val.replace('_','').replace('.','').lower()
			if val == enc:
				return val
		
		# find aliase in encodings.aliases.aliases dict
		EAA = encodings.aliases.aliases
		for a in EAA:
			val = EAA[a]
			val = val.replace('_','').replace('.','').lower()
			if val == enc:
				return val
		
	
	
	#
	# UTILITY
	#
	
	def validate(self, enc):
		"""
		Check that `enc` matches either DEF_ENCODE, one of the ENCODINGS,
		or something in the encodings.aliases.aliases dict.
		
		The `strict` constructor arg has a strong effect on results. If
		strict, the given `encoding` must *exactly* match a value from
		
		Result is always an item from ENCODINGS, or raised ValueError. 
		"""
		if not enc:
			return enc
		
		gvn = enc
		enc = enc.lower()
		
		if not self.__strict:
			enc = enc.replace("-","_").lower()
			if enc == DEF_ENCODE:
				return enc
		
		# strict results (ENCODINGS or aliases)
		if enc in ENCODINGS:
			return enc
		if enc in encodings.aliases.aliases:
			return encodings.aliases.aliases[enc]
		
		# wild (close-match to strict results)
		if not self.__strict:
			enc = self.altalias(enc)
			if enc:
				return enc
		
		raise ValueError("err-invalid-encoding", xdata(
			reason="unknown-encoding", detail="no-matching-alias",
			encoding=gvn, strict=True if self.__strict else False
		))
	
	def match(self, encoding):
		"""True if `encoding` matches self.encoding (or an alias)."""
		return self.validate(encoding) == self.encoding
	
	def encode(self, s):
		"""Encode to bytes (if not already bytes). Returns bytes."""
		try:
			return s.encode(**self.__ek)
		except AttributeError:
			return s # s is already bytes
	
	def decode(self, b):
		"""Decode to unicode (if not already unicode). Returns unicode."""
		try:
			return b.decode(**self.__ek)
		except AttributeError:
			return b # b is already unicode
	
	def mcode(self, mode, data):
		"""Encode or decode based on `mode`."""
		return self.encode(data) if 'b' in mode else self.decode(data)




#
# ENCODING DATA
#

ENCODINGS = [
	'ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 
	'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 
	'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 
	'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 
	'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 
	'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 
	'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 
	'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 
	'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 
	'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 
	'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 
	'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 
	'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 
	'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 
	'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 
	'shift_jis_2004', 'shift_jisx0213', 'utf_32', 'utf_32_be', 
	'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 
	'utf_8_sig'
]

# Encodings with a byte order mark
ENCODINGS_W_BOM = [
		'utf_32', 'utf_32_be', 'utf_32_le','utf_16', 'utf_16_be', 
		'utf_16_le'
	]


#
# I know these have BOMs, but I can't figure out how to check them
#
ENCODINGS_W_BOM_I_CAN_NOT_PARSE = [
	'utf_7', 'gb18030'
]

