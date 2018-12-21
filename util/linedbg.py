

from ..fmt import *

class linedbg(object):
	
	def __init__(self):
		self.jformat = JDisplay()
	
	def dbg (self, *a, **k):
			
		# title			
		print ("\n#\n# DEBUG:")
		
		#
		# ITEMS/LINES 
		#  - Is this really needed? maybe we should check **k for args...
		#    There's not much sense in duplicating it.
		#
		for item in list(a):
			lines = str(item).splitlines()
			for line in lines:
				print ("# * %s" % str(line))
		
		# extra data passed as kwargs
		if k:
			lines = self.jformat(k).splitlines()
			for line in lines:
				print ("# %s" % str(line))
		
		# xdata
		if trix.tracebk():
			self.print_xdata(xdata())
			
		# end
		print ("#\n")
	
	
	def print_xdata(self, xdata=None):
		xd = self.jformat(xdata).splitlines()
		if xd:
			print ("#\n# xdata:")
			for item in xd:
				ll = item.splitlines()
				for line in ll:
					print ("# %s" % str(line))
	
