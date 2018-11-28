#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import time

def cache(maxsize=512, timeout=9):
	"""
	Returns a new Cache object. Use a cache to store the results of 
	calculations/operations that take a long time to complete.
	
	Argument `maxsize` limits the number of items that may be stored
	in the Cache object simultaneously. It defaults to 512 items. If 
	The item data is extremely large, it may be best to pass a lower
	number. If the expected data items are very small and numerous, a
	larger number may be appropriate.
	
	The timeout argument causes items that have been in the cache for
	more seconds than its specified value to be removed (on the next
	call to `set` or `get`.	The default timeout value of 9 seconds was 
	chosen to suit looping functions that don't won't take a long time 
	to complete (specifically, string scanning functions). If you expect
	your operation to last longer and require the use of items given 
	earlier at later times in the processing, it may be wise to increase
	the timeout value.
	
	```python3
	>>> c = cache()
	>>> c.set('foo', 'bar')
	>>> c.get('foo')
	'bar'
	```
	"""
	return Cache(maxsize=maxsize, timeout=timeout)


#
#
# CACHE OBJECT
#
#
class Cache(object):
	"""Cache keyed values short-term. Use for expensive lookups."""
	
	def __init__(self, **k):
		"""Kwargs timeout and maxsize (of dict) might be useful."""
		
		self.__k = k
		self.__cache = {}
		self.__counted = {}
		self.__counter = 0
	
	
	@property
	def count(self):
		"""The number of items in the cache."""
		return len(self.__cache)
	
	@property
	def timeout(self):
		"""The lifespan for cached items, after which they're removed."""
		return self.__k.get('timeout')
	
	@property
	def maxsize(self):
		"""
		The maximim number of items allowed in the cache. Once reached,
		items set earlier in will be deleted so that the maximimum size 
		is honored.
		"""
		return self.__k.get('maxsize')
	
	
	# SET
	def set(self, key, value):
		"""Pass a `key` and a `value` for storage (or replacement)."""
		idnum = self.__counter
		vdict = dict(value=value, ncount=idnum, time=time.time())
		self.__cache[key] = vdict
		self.__counted[idnum] = key
		self.__counter += 1
		return self.cleanup()
	
	
	# GET
	def get(self, key):
		"""Pass a `key`; the value is returned (or KeyError raised)."""
		try:
			self.__cache[key][time] = time.time()+self.__k.get('timeout',0)
			return self.__cache.get(key,{}).get('value')
		finally:
			self.cleanup()
	
	
	# ADD
	def add(self, key, value):
		"""
		Add is an alias for set, but raises an exception if the given key
		already exists.
		"""
		if key in self.__cache:
			raise Exception('err-add-fail', xdata(
					reason='duplicate-key', key=key, value=value
				))
		return self.set(key, value)
	
	
	# CLEANUP
	def cleanup(self):
		"""
		Cleanup is performed automatically after every `get` or `set`.
		It may be called manually any time if you want to flush timed-out
		items (just for fun, or whatever).
		"""
		# timeout cleanup first
		tolist = []
		timeout = self.__k.get('timeout')
		for k in self.__cache:
			if time.time() > (self.__cache[k]['time'] + timeout):
				tolist.append(k)
		
		for k in tolist:
			if k in self.__cache:
				idnum = self.__cache.get(k,{}).get('idnum')
				if idnum != None:
					del(self.__counted[idnum])
					del(self.__cache[k])
		
		# max-size cleanup last
		maxsize = self.__k.get('maxsize')
		dictlen = len(self.__counted)
		if maxsize and (dictlen > maxsize):
			rcount = dictlen - maxsize
			skeys = sorted(self.__counted.keys())
			ckeys = list(skeys[:rcount])
			for ckey in ckeys:
				try:
					del(self.__cache[self.__counted[ckey]])
					del(self.__counted[ckey])
				except KeyError:
					pass


