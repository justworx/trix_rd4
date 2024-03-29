#
# Copyright 2014-2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import gc
from collections import defaultdict
from trix import *

#
# RIGHT... this is all wrong. It doesn't work. 
# 
# Apparently it's not finding changes since the last check, but is
# just adding 1 of each object each time get() is called (resulting
# in a doubling of whatever the previous count for any given object
# had been).
#
# Obviously, this is useless. What I'm looking for is:
# [CURRENT COUNT] - [START COUNT] for each existing class.
# 
# I don't think the fix is going to happen tonight. Too sleepy.
# Probably need to rebuild from a fresh copy from the original 
# source.
#


class Profile(object):
	"""
	Track objects created during runtime.
	"""
	
	# INIT
	def __init__(self, **kwargs):
		"""
		Profile names/counts of objects created starting with this
		object's creation.
		"""
		self.__start = defaultdict(int)
		for o in gc.get_objects():
			self.__start[self.__key(o)] += 1
	
	
	# GET-OBJECTS
	def __getobjects(self):
		"""
		This seems to be returning a dict containing a current count of
		each object type... apparently for comparison to previous counts
		of the object.
		"""
		currentObjects = defaultdict(int)
		for o in gc.get_objects():
			currentObjects[self.__key(o)] += 1
		return currentObjects
	
	
	# CURRENT
	def __current(self):
		"""
		Generates list of all objects currently in memory.
		"""
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
		"""
		Return True if key `k` starts with a prefix given to constructor
		as selectable.
		"""
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
		"""
		Returns a (usually large) dict of objects/counts that were in 
		memory at the time of this Profile object's creation.
		"""
		return self.__start
	
	
	@property
	def current(self):
		"""Returns a dict of objects/counts in memory now."""
		return self.__current()
	
	
	def get(self):
		"""
		Returns a dict containing counts of objects created between this 
		profile's creation (self.start) and the current set of objects,
		(self.current).
		"""
		r = {}
		cur = self.__current()
		for s in cur:
			if s in self.__start:
				ct = cur[s] - self.__start[s]
				if (ct > 0) and self.__opt_show(s):
					r[s] = ct
		return r
	
	
	def display(self):
		"""
		Display in JDisplay format all objects created since this 
		Profile's creation.
		"""
		trix.display(self.get())
	
	
	# SEARCH
	def searchall(self, s):
		"""
		Search all objects starting with a given string value `s`. 
		Returns dict with module/class key and count value.
		"""
		d = self.__getobjects()
		r = {}
		for k in d:
			if k.startswith(s):
				r[k] = d[k]
		return r
