#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from collections import deque
from .xqueue import *


class fifo(object):
	"""First-in/First-out stack."""
	
	def __init__(self):
		"""Pass any initial items to push"""
		self.__queue = Queue()
		self.push = self.__queue.put_nowait
		self.pop = self.__queue.get_nowait


class lifo(object):
	"""Last-in/first-out stack."""
	def __init__(self):
		self.__xx = lifo_deque()
		self.push = self.__xx.push
		self.pop = self.__xx.pop
	
	# for debugging...
	#@property
	#def xx(self):
	#	return self.__xx


#
# LIFO HANDLERS
#
class lifo_deque(object):
	"""Deque list. Fastest."""
	def __init__(self):
		self.__deque = deque()
		self.push = self.__deque.append
		self.pop = self.__deque.pop


# SUPER-SLOW
class lifo_queue(object):
	"""
	This one is very slow. Don't use it unless there's some threading
	(or other timing) issue.
	"""
	def __init__(self):
		self.__queue = Queue()
		self.push = self.__queue.put_nowait
		self.pop = self.__queue.get_nowait


"""
#
# PRE-2.4 
#  - Ya, this will probably never be used, but I want to know where it
#    is just in case I ever need it.
#  - Note that it's significantly faster then lifo_queue, but slower
#    than lifo_deque.
#
class lifo_list(object):
	# Backup, for pre 2.4 python versions.
	def __init__(self):
		self.__stack = []
		self.push = self.__stack.append
	
	def pop(self):
		try:
			return self.__stack[-1]
		finally:
			del(self.__stack[-1])
"""
