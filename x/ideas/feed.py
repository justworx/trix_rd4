#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from trix import *


class Feed(object):
	"""Feed data to a given target."""
	
	def __init__(self, targets=None):
		"""Pass optional list of FeedTarget objects."""
		self.__targets = targets or []
	
	def feed(self, data):
		"""Feed the given data to each target."""
		for targ in self.__targets:
			targ.feed(data)
	
	def set(self, target):
		"""Add a new FeedTarget object.""" 
		self.__targets.append(target)
	
	def remove(self, fed):
		"""Remove the given `fed` FeedTarget object."""
		self.__targets.remove(fed)




class FeedTarget(object):
	"""
	Manages a feed connection.
	
	FeedTarget does nothing on it's own. Use subclasses FeedFile,
	FeedSock, and FeedTerm to feed data to a subscriber object as
	text (default: compact json format).
	"""
	
	def __init__(self, feeder, *a, **k):
		"""
		Pass feeder and any formatting args/kwargs (for trix.formatter).
		The reason for this Feed system is to transfer data to external
		objects, so the default format is JCompact.
		"""
		self.__feeder = feeder
		self.formater = trix.formatter(*a, **k)
	
	def close(self):
		"""
		Close this FeedTarget object. It will be removed from the Feed
		object and deleted. This target will receive no more feeds.
		"""
		self.feeder.remove(self)




class FeedTerm(FeedTarget):
	"""Default FeedTarget prints data."""
	
	def feed(self, data):
		"""Accept "fed" data. Default action: print data."""
		self.formater.output(data)




class FeedFile(FeedTarget):
	"""Feed data to a text file."""
	
	def __init__(self, feeder, path, **k):
		"""Pass feeder, file path, and optional kwargs."""
		FeedTarget.__init__(self, feeder)
		self.__newl = k.get('newl', '\r\n')
		self.__file = trix.path(path).wrapper(**k)
	
	def feed(self, bytedata):
		"""Write `bytedata` to the file given to the constructor."""
		self.__file.send(self.formater.format(data) + self.__newl)




class FeedSock(FeedTarget):
	"""Write data to a socket."""
	
	def __init__(self, feeder, sock, **k):
		FeedTarget.__init__(self, feeder)
		self.__k    = k
		self.__sock = sock
	
	def feed(self, data):
		"""Feed data through a socket."""
		
		data = self.formater.format(data)
		try:
			bytedata = data.encode(**self.__k)
		except Exception as ex:
			bytedata = data
		
		self.__sock.send(bytedata)


