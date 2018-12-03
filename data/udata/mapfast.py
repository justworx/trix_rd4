#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from . import *


#
# PROPFAST
#  - Fast property lookups.
#
class mapfast(object):
	"""
	Fast codepoint property lookup.
	
	Builds an index from a unicode data dict with keys that are strings
	(such as property names) and values that are lists of either single
	integers or integer pairs (ranges).
	"""
	
	@property
	def blocks(self):
		"""The data for all blocks/properties."""
		return self.__fblocks
	
	@classmethod
	def gblocks(cls):
		"""Block name generator."""
		for b in udata.blocknames():
			yield (b)
	
	
	def __init__(self, unicode_data_dict):
		"""
		Build an index from a unicode data dict with keys that are strings
		such as property names and values that are lists of either single
		integers or integer pairs (ranges).
		"""
		self.__dict = unicode_data_dict
		self.__keys = sorted(self.__dict.keys())
		
		self.__fblocks = {}
		self.__addblocks()
		self.__addprops()
	
	
	@property
	def dict(self):
		return self.__dict
	
	@property
	def keys(self):
		return self.__keys
	
	@property
	def fblocks(self):
		return self.__fblocks
	
	
	def __addblocks(self):
		for block in self.gblocks():
			self.__fblocks[block] = {}
	
	
	def __addprops(self):
		
		for block in self.__fblocks.keys():
			
			# get the range for this block
			br = udata.blocks()[block]
			brange = range(br[0],br[1]+1)
			
			#
			# Loop through each property name; add a custom property list
			# just for this particular block.
			#
			
			for propname in self.keys: #eg, PROPERTIES.keys():
				self.__fblocks[block][propname] = []
				proplist = self.dict[propname]
				for prop in proplist:
					try:
						p1 = prop[0]
						pn = prop[1]
						if (p1 in brange) and (pn in brange):
							self.__fblocks[block][propname].append(prop)
					except:
						if prop in brange:
							self.__fblocks[block][propname].append(prop)
				
				# don't hang on to empty property sets
				if not self.__fblocks[block][propname]:
					del(self.__fblocks[block][propname])


	
	
	def propgen(self, c):
		"""Loop through each property list for `c` property matches."""
		
		# result storage
		rr = []
		
		# find the block that contains the given codepoint
		cblock = udata.block(c)
		
		# store the dict of all blocks/properties locally (for speed)
		FB = self.fblocks
		
		# store the dict `bprops` locally (for speed)
		bprops = FB[cblock]
		
		# gotta use int, not chr
		x = ord(c)
		
		# localize callables for speed improvement
		isinst = isinstance
		
		# loop through proplists; yield matching properties in `rr`
		for propname in self.keys:
			try:
				
				# get the list of codepoints with the current `propname`
				proplist = bprops[propname]
				
				# testing this - seems to work well and is a bit faster
				if is_in_unicode_range_list(ord(c), proplist):
					yield (propname)
				
				"""
				# this works; we'll do some more testing before removing it
				for i in proplist:
					if ((x==i) if isinst(i,int) else x>=i[0] and x<=i[1]):
						# there's only one linebreak property per character
						yield (propname)
				"""
			except KeyError:
				pass
		return rr




	
	
	def display(self, **k):
		"""Display a (very long) list of block values in a fmt.Grid."""
		
		# loop through block names
		for blockname in sorted(self.__fblocks.keys()):
			
			# Print block name in all-caps
			print ("\n\n#\n# %s\n#" % (blockname.upper()))
			
			# loop, appending items to prop list `bp`
			bp = []
			for propname in self.__fblocks[blockname]:
				for items in self.__fblocks[blockname][propname]:
					bp.append([propname, ":", items])
			
			# show it in a grid
			if bp:
				trix.display(bp, f='Grid', **k)



#
# Try to mix this into `propgen`, above, where it currently loops 
# through all blocks in order. Might speed things up a little.
#
def is_in_unicode_range_list(char_code, range_list):
	"""
	Binary search on ordered lists (such as those sometimes used in
	the unicode database) that contain items that may be integers or
	lists containing a minimum and a maximum to represent a range. 
	
	Thanks again to jotun for this speed-up.
	"""
	first = 0
	last = len(range_list) - 1
	isinst = isinstance

	while first <= last:
		i = int((first + last) / 2)
		current = range_list[i]
		
		if isinst(current, int):
			if current == char_code:
				return True
			elif current > char_code:
				last = i - 1
			else:
				first = i + 1
		else:
			if current[0] <= char_code <= current[1]:
				return True
			elif current[1] > char_code:
				last = i - 1
			else:
				first = i + 1
	return False


