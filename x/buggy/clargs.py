#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

import sys


class clargs(object):
	"""
	Parse a line of text to a dict containing args, kwargs, and flags.
	
	The trix package uses a specific standard for parsing text 
	commands. It's different from both *nix and Windows command 
	line formats, but should facilitate both. 
	
	 * Anything prefixed with "--" is added to a dict used to provide
	   keyword arguments to a function or method. The kwarg must be
	   given in the format "--name=value"
	 * Any character string prefixed with a single dash "-" is taken
	   as a list of boolean flags.
	 * All other string values are taken, in the received order, as 
	   individual arguments.
	
	NOTE that this is not intended as an all-inclusive method for 
     passing arguments. Any args or kwargs must be a single string,
     so it's not a straightforward process to pass.
     
     For example: passing "--list=dog cat mouse" to `clargs` will
     result in {"kwargs":{'list':'dog'}, "args":['cat', 'mouse']}  
     
     This is true for any command line argument (either from a
     shell, or via a shell-like system such as `app.console`.
     
     When complex arguments are needed, the values will may be
     compressed to a non-breaking string (eg, base64) before being
     passed as an 'arg' or 'kwarg'.
	"""
	
	def __init__(self, offset=0):
		"""
		Pass an offset (default: 0) that marks the beginning of command
		line items (split on ' ' space) to be parsed. For example, the
		trix.app.cline class would start at offset 3 to receive arguments
		['alpha3:', 'A', 'B', 'C'] while ignoring the "python -m trix" 
		part of the original command line.
		
		$ python3 -m trix alpha3: A B C
		"""
		
		self.offset = offset
		self.args = []
		self.flags = ''
		self.kwargs = {}
	
	
	def parse (self, text):
		self.args = sys.argv[self.offset]
		self.flags = ''
		self.kwargs = {}
		
		for a in self.args:
			if a[:2]=="--":
				kv = a[2:].split("=")
				self.kwargs[kv[0]] = kv[1] if len(kv)>1 else True
			elif a[:1] == '-':
				self.flags += a[1:]
			else:
				self.args.append(a)
		
		return {'args':self.args,'kwargs':self.kwargs,'flags':self.flags}



