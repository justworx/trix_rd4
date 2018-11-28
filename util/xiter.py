#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from .. import *


class xiter(object):
	"""Cross-version iterator support."""
	
	def __init__(self, iteratable):
		self.__iteratable = iteratable
	
	def __iter__(self):
		return iter(self.__iteratable)
	
	def __next__(self):
		return next(self.__iteratable)
	
	def next(self):
		try:
			return self.__next()
		except AttributeError:
			xd1 = xdata()
			try:
				self.__next = self.__next__
				return self.__next()
			except AttributeError:
				xd2 = xdata()
				try:
					self.__next = self.__iteratable.next
					return self.__next()
				except:
					raise Exception('err-iter-fail', xdata(
							iterable=self.__iteratable, T=type(self.__iteratable),
							xd1=xd1, xd2=xd2
						))


