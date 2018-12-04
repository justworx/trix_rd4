#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from . import *
from ...util.compenc import *

class compenc(cline):
	"""
	Compression/Encoding.
	
	$ python3 -m trix compenc compact Test! This is a test.
	"""
	def __init__(self):
		cline.__init__(self)
		
		krg = self.kwargs
		enc = krg.get('encoding', krg.get('enc', 'utf_8'))
		
		if 'compact' in self.kwargs:
			ctext = compact(self.kwargs.get('compact'))
			try:
				ctext = ctext.encode(enc)
			except:
				pass
			print ("compact: %s" % ctext.decode(enc))
		elif 'expand' in self.kwargs:
			etext = expand(self.kwargs.get('expand'))
			try:
				etext = etext.encode(enc)
			except:
				pass
			print ("expand: %s" % etext.decode(enc))
		
		else:
			# make sure arg is encoded to bytes
			arg = self.args[0]
			try:
				arg = arg.encode(enc)
			except:
				pass
			
			# encode
			if 'e' in self.flags:
				print ('base64: %s' % b64.encode(arg).decode(enc))
				print ('base32: %s' % b32.encode(arg).decode(enc))
				print ('base16: %s' % b16.encode(arg).decode(enc))
				print ('hex   : %s' % hex.encode(arg).decode(enc))
				print ('zlib  : %s' % zlib.encode(arg))
				print ('bz2   : %s' % bz2.encode(arg))
			
			# decode
			else:
				i=0
				try:
					print ('base64: %s' % b64.decode(arg).decode(enc))
					i += 1
				except:
					pass
				
				try:
					print ('base32: %s' % b32.decode(arg).decode(enc))
					i += 1
				except:
					pass
				
				try:
					print ('base16: %s' % b16.decode(arg).decode(enc))
					i += 1
				except:
					pass
				
				try:
					print ('hex   : %s' % hex.decode(arg).decode(enc))
					i += 1
				except:
					pass
				
				
				# I don't know what to do with these...
				"""
				try:
					print ('zlib: %s' % zlib.decode(arg))
					i += 1
				except:
					pass
				
				try:
					print ('bz2: %s' % bz2.decode(arg).decode(enc))
					i += 1
				except:
					pass
				"""
				
				
				#
				if not i:
					print ("No results.")
		
