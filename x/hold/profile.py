"""
Copyright 2014-2015 Troy Hirni
This file is part of the aimy project, distributed under
the terms of the GNU Affero General Public License.

Profile garbage collection.
"""

from collections import defaultdict
import gc, time


class Profile(object):
	
	# INIT
	def __init__(self, **kwargs):
		
		self.__options = {}
		for k in kwargs:
			self.__options[k] = kwargs[k].split()
		
		self.__last = {}
		self.__start = defaultdict(int)
		for o in gc.get_objects():
			self.__start[self.__key(o)] += 1
	
	
	# GET-OBJECTS
	def __getobjects(self):
		currentObjects = defaultdict(int)
		for o in gc.get_objects():
			currentObjects[self.__key(o)] += 1
		return currentObjects
	
	
	# CURRENT
	def __current(self):
		newObjects = defaultdict(int)
		for o in gc.get_objects():
			newObjects[self.__key(o)] += 1
		return newObjects
	
	
	# KEY
	def __key(self, o):
		try:
			return "%s.%s" % (o.__module__, o.__name__)
		except:
			return str(type(o))
	
	
	# OPT-SHOW
	def __opt_show(self, k):
		if 'prefix' in self.__options:
			for s in self.__options['prefix']:
				if k.startswith(s):
					return True
			return False
		elif 'limit' in self.__options:
			return k in self.__options['limit']
		return True
	
	
	@property
	def options(self):
		return self.__options
	
	
	@property
	def start(self):
		return self.__start
	
	
	@property
	def current(self):
		return self.__current()
	
	
	@property
	def get(self):
		r = {}
		cur = self.__current()
		for s in cur:
			if s in self.__start:
				ct = cur[s] - self.__start[s]
				if (ct > 0) and self.__opt_show(s):
					r[s] = ct
		return r
	
	
	# SEARCH
	def searchall(self, s):
		d = self.__getobjects()
		r = {}
		for k in d:
			if k.startswith(s):
				r[k] = d[k]
		return r
		


#
# UNDER CONSTRUCTION!
#
class tcheck(object):
	"""
	This can be handy, but note that there are 
	a lot of changes needed (and coming).
	"""
	Tabs = 0
	def __init__(self, L='', **kwargs):
		self.__tab = kwargs.get('tab', ' ')
		self.__label = kwargs.get('label', L)
		self.__start = None
		self.start()
	
	def start(self):
		if not self.__start:
			tcheck.Tabs = tcheck.Tabs + 1
		self.__start = time.time()
	
	def stop(self):
		print self.__label, time.time()-self.__start
		tcheck.Tabs = tcheck.Tabs - 1
	
	@property
	def tab(self):
		if tcheck.Tabs < 0:
			tcheck.Tabs = 0
		return self.__tab * (tcheck.Tabs-1) if tcheck.Tabs > 0 else ''

