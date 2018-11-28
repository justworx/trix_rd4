#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .. import *


class Opener(object):
	"""Manage file opening."""
	
	@classmethod
	def open(cls, path, mode=None, **k):
		try:
			return cls.__open(path, mode or 'r', **trix.kcopy(k, cls.__kk))
		except AttributeError:
			cls.__open = cls.best()
			return cls.__open(path, mode or 'r', **trix.kcopy(k, cls.__kk))
	
	@classmethod
	def kk(cls):
		try:
			return cls.__kk
		except AttributeError:
			cls.__open = cls.best()
			return cls.__kk
		
	
	@classmethod
	def opener(cls):
		try:
			return cls.__open
		except AttributeError:
			cls.__open = cls.best()
			return cls.__open
	
	# call these to specifically set an open method
	@classmethod
	def setiopen(cls):
		cls.__kk = "encoding errors buffering newline closefd"
		cls.__open = trix.value('io.open')
		return cls.__open
	
	@classmethod
	def setcopen(cls):
		cls.__kk = "encoding errors buffering"
		cls.__open = trix.value('codecs.open')
		return cls.__open
	
	@classmethod
	def setoopen(cls):
		cls.__kk = "buffering"
		cls.__open = open
		return cls.__open
	
	@classmethod
	def setfopen(cls):
		cls.__kk = ""
		cls.__open = file
		return cls.__open
	
	# call this to find the best available open method
	@classmethod
	def best(cls):
		try:
			return cls.__best
		except AttributeError:
			#
			# cls.__best is not yet set - find the most current available
			# file-opening function.
			#
			try:
				# try io
				cls.__best = cls.setiopen()
				return cls.__best
			except AttributeError as ex:
				try:
					# try codecs
					cls.__best = cls.setcopen()
					return cls.__best
				except AttributeError as ex:
					try:
						cls.__best = cls.setoopen()
						return cls.__best
					except AttributeError as ex:
						cls.__best = cls.setfopen()
						return cls.__best
	
	

