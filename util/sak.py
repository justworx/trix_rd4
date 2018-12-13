#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import *

class sak(object):
	
	@classmethod
	def filter(cls, key, **k):
		"""
		Pass zero or more kwargs from ['prefix', 'suffix', 'contains'];
		Any criteria given must be matched for a True return value. If
		no criterion is given, result is True.
		
		FILTERS (by keyword argument) are cumulative.
		 * prefix : results must start with prefix.
		 * suffix : results must end with suffix.
		 * contains: results must contain the given kwarg's value.
		"""
		show = True
		if k.get('prefix'):
			show = show and key.startswith(k.get('prefix'))
		if k.get('suffix'):
			show = show and key.endswith(k.get('suffix'))
		if k.get('contains'):
			show = show and (k.get('contains') in key)
		return show
	
	
	@classmethod
	def modlist(cls, **k):
		"""
		List loaded modules (with optional filters). Good for	debugging.
		"""	
		keys = sorted(sys.modules.keys())
		fstr = " * {:<25} : {}"
		
		for key in keys:
			# display (if filters did not prevent)
			if cls.filter(key, **k):
				print(fstr.format(key, sys.modules[key]))
	
	
	@classmethod
	def odir(cls, o, *a, **k):
		"""
		Pass an object - it's sorted __dir__ list is presented in a i'table.
		Pass optional keyword arguments as accepted by Table. (Eg, width.)
		"""
		k.setdefault("width", 3)
		r = []
		for x in sorted(o.__dir__()):
			if cls.filter(x, **k):
				r.append(x)
		trix.display(r, f='Table', **k)
	
	
	@classmethod
	def odict(cls, o, method):
		"""Pass object and property name; returns the property object."""
		return o.__dict__[method]
	
	



