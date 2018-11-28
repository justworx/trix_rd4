#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


class checkrange(object):
	
	xVAL = 'err-invalid-value'
	xMIN = 'err-below-minimum'
	xMAX = 'err-above-maximum'
	
	def __init__(self, minimum, maximum):
		"""Specify `minimum` and `maximum` range."""
		self.__min = minimum
		self.__max = maximum
	
	
	def check(self, val, **k):
		"""Raise ValueError if `val` is outside range."""
		if self.__min and (val < self.__min):
			raise ValueError(cls.xVAL, xdata( 
				value=val, reason=cls.xMIN, max=self.__max, min=self.__min
			))
		
		if self.__max and (val > self.__max):
			raise ValueError(cls.xVAL,  xdata(
				value=val, reason=cls.xMAX, max=self.__max, min=self.__min
			))
		return value
	
	__call__ = check # might as well...
		
