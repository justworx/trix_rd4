

from trix.util.output import *

class fio(object):
	def __init__(self, fn):
		self.__fn = fn
	
	def output(self, *a, **k):
		return self.__fn(*a, **k)

