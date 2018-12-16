#
# Copyright 2014-2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from trix import *
from collections import defaultdict
import gc


class Profile(object):
	"""
	Track objects created during runtime.
	"""
	
	# INIT
	def __init__(self, **kwargs):
		"""Generate 'start' list and process/store options."""
		
		# get original starting set of in-memory objects
		self.__start = defaultdict(int)
		for o in gc.get_objects():
			self.__start[self.__key(o)] += 1
	
	
	# GET-OBJECTS
	def __getobjects(self):
		"""
		Get the set of objects in memory right now.
		"""
		currentObjects = defaultdict(int)
		for o in gc.get_objects():
			currentObjects[self.__key(o)] += 1
		return currentObjects
	
	
	# CURRENT
	def __current(self):
		"""Generates list of all objects currently in memory."""
		newObjects = defaultdict(int)
		for o in gc.get_objects():
			newObjects[self.__key(o)] += 1
		return newObjects
	
	
	# KEY
	def __key(self, o):
		"""
		Utility for generating display name (module.classname). Returns
		only classname for builtin classes.
		"""
		try:
			return "%s.%s" % (o.__module__, o.__name__)
		except:
			return str(type(o))
	
	
	@property
	def start(self):
		"""
		Returns a dict of objects/counts that were in memory at the time
		of this Profile object's creation.
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
