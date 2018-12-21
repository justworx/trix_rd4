#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import * # fnload, enchelp, trix.*


#
# --- BYTE 'COMPRESSION/ENCODING' CLASSES ---
#

#
# ENCODERS
#  - These Loader-based classes don't import their respective modules
#    until one of their methods is called.
#

class b64():
	encode = Loader('base64', 'b64encode')
	decode = Loader('base64', 'b64decode')
	sencode = Loader('base64', 'standard_b64encode')
	sdecode = Loader('base64', 'standard_b64decode')
	uencode = Loader('base64', 'urlsafe_b64encode')
	udecode = Loader('base64', 'urlsafe_b64decode')

class b32():
	encode = Loader('base64', 'b32encode')
	decode = Loader('base64', 'b32decode')

class b16():
	encode = Loader('base64', 'b16encode')
	decode = Loader('base64', 'b16decode')

class hex():
	encode = hexlify = Loader('binascii', 'hexlify')
	decode = unhexlify = Loader('binascii', 'unhexlify')

#	COMPRESSION
class zlib():
	encode = compress = Loader('zlib', 'compress')
	decode = decompress = Loader('zlib', 'decompress')

class bz2():
	encode = compress = Loader('bz2', 'compress')
	decode = decompress = Loader('bz2', 'decompress')


#
# FUNCTIONS
#  - Custom compact/expand functions.
#  - The purpose of compact is NOT to make `data` smaller, but to make
#    it portable in as small a package as possible. The original
#    purpose for this was to send command line arguments safely
#    when creating remote processes.
#

def compact(data, encoding=DEF_ENCODE):
	"""
	Compact bytes using zlib.compress, then b64.encode. Use `expand` to
	retreive these compacted bytes. If `data` is given as unicode text,
	pass the encoding (or default DEF_ENCODE is used).
	
	NOTE: The purpose here is not to make `data` smaller, but to make 
	      it portable (in as compact a package as possible).
	"""
	try:
		return b64.encode(zlib.compress(data))
	except:
		return b64.encode(zlib.compress(data.encode(encoding)))
		

# EXPAND
def expand(data, encoding=DEF_ENCODE):
	"""
	Expand `data` previously compressed by `compact`.
	
	NOTE: Always returns bytes! The encoding argument is used only in
	      cases where `data` is given as unicode text rather than
	      bytes. The caller must decode to unicode.
	"""
	try:
		return zlib.decompress(b64.decode(data))
	except:
		return zlib.decompress(b64.decode(data.encode(encoding)))

