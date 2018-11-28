#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

import codecs


def testbom(bytestring):
	"""
	Detect encoding based on byte order mark. UTF-32, UTF-16, UTF-8-SIG
	"""

	b32 = len(codecs.BOM_UTF32_LE)
	b16 = len(codecs.BOM_UTF16_LE)
	b8 = len(codecs.BOM_UTF8)
	
	# try the u32 encodings
	if bytestring[:b32] == codecs.BOM_UTF32_LE:
		return 'utf_32_le'
	elif bytestring[:b32] == codecs.BOM_UTF32_BE:
		return 'utf_32_be'
	
	# try the u16 encodings
	elif bytestring[:b16] == codecs.BOM_UTF16_LE:
		return 'utf_16_le'
	elif bytestring[:b16] == codecs.BOM_UTF16_BE:
		return 'utf_16_be'
	
	# utf-8-sig
	elif bytestring[:b8] == codecs.BOM_UTF8:
		return 'utf_8_sig'
	
	
	#
	# I don't know how to make these work. They're from wikipedia.
	#  - https://en.wikipedia.org/wiki/Byte_order_mark#Byte_order_marks_by_encoding
	#
	# More:
	#  - https://en.wikipedia.org/wiki/Talk%3AByte_order_mark
	#  - http://www.thefullwiki.org/GB18030
	#
	"""
	# gb-18030
	elif bytestring[:4] == [0x84, 0x31, 0x95, 0x33]:
		return 'gb18030'
	
	# utf-7
	elif bytestring[:3] == [0x2b, 0x2f, 0x76]:
		# first three bytes are always 2B 2F 76
		b45 = self.__bb[4:5]
		if (b45[0] in [0x38,0x39,0x2b,0x2f]):
			return 'utf-7'
	"""
	
