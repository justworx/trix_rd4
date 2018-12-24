#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *


class Counter(object):
	"""
	DEBUGGING TOOL - Count steps through tracking process.
	"""
	
	def  __init__(self, **k):
		"""Pass initial count (default 0) by kwarg 'ct'."""
		self.__ct = k.get('ct', 0)
	
	def next(self):
		"""Add one tracking step; Return new value."""
		self.__ct += 1
		return self.__ct



class Tracker(Counter):
	"""
	DEBUGGING TOOL - Track location of steps along complicated paths.
	
	Keyword args:
	 * ct - Initial count for locations - Default 0.
	
	The point of Tracker is to trace through a complicated set of
	method calls, recording the step number and call stack at each
	step. You must add a call to Tracker.track() at each location 
	along the path. You are really the tracker... Tracker() is your
	way of examining the tracks at each point. 
	
	Start at the place where it seems things are working right. At
	each step, place a call to Tracker.track().
	
	Run the code from the python interpreter, then call 
	Tracker.display(). A dict is displayed in which keys are integers
	- sorted ascending - that give you the accurate position of each
	calls.
	
	In complicated situations, the order of calls may not be as you
	might expect, but within a given thread Tracker always displays
	calls in the order they occur.
	"""
	
	def __init__(self, **k):
		Counter.__init__(self, **k)
		self.__tracks = {}
	
	def __call__(self, *a):
		self.track(*a)
	
	@property
	def tracks(self):
		return self.__tracks
	
	def track(self, *a):
		#trace = [traceback.extract_stack()]
		trace = [traceback.extract_stack()]
		if a:
			trace.extend(a)
		self.__tracks[self.next()] = trace
	
	def display(self):
		trix.display(self.__tracks, sort_keys=1)
	


