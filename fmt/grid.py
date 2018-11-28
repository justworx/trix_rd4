#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *


class Grid (FormatBase):
	"""
	Format list of lists into a grid.
	
	>>> grid.Grid().output(list([1,2],[3,4]))
	"""
	
	def __init__(self, **k):
		"""
		Kwarg `sep` defaults to a single space; Optional `cellformat` 
		kwarg specifies a callable to apply to each cell (default: str).
		"""
		self.__ind = k.get('indent', "")
		self.__fmt = k.get('cellformat') or str
		self.__sep = k.get('sep', FORMAT_SEP)
		self.__tsep = k.get('tsep', ':')
		FormatBase.__init__(self)
		
		# experimental
		self.__out = k.get('output')
	
	
	def formatstring(self, grid):
		"""Generate a format string for the given grid."""
		glen = len(grid[0])
		cmax = [0 for x in range(glen)]
		for row in grid:
			for c,col in enumerate(row):
				L = len(col)
				if L > cmax[c]:
					cmax[c] = L
		
		fstr = map(lambda x: "{:<%s}" % x, [cmax[x] for x in range(0, glen)])
		return self.__sep.join(fstr)
	
	
	def formatgrid(self, grid, fmt):
		"""Duplicate grid, but with each item formatted by fmt."""
		
		# duplicate grid with formatted items
		fgrid = []
		for gRow in grid:
			cols = []
			for col in gRow:
				# copy each cell from grid to fgrid, but formatted
				cols.append(fmt(col))
			fgrid.append(cols)
		
		# return the copy
		return fgrid
	
	
	def format(self, grid, **k):	
		
		# format grid
		ind = k.get("indent", self.__ind)
		fmt = k.get("cellformat", self.__fmt)
		if fmt:
			grid = self.formatgrid(grid, fmt)
		
		r = []
		f = self.formatstring(grid)
		try:
			for row in grid:
				r.append("%s%s" % (ind, f.format(*row)))
		except Exception:
			xd = xdata(
				error='err-grid-format', fmt=f, row=row, grid=grid[:3]
			)
			raise xd['xtype'] (xd)
		
		return '\n'.join(r)






class List(Grid):
	"""
	Simple list formatter - displays a list's items in individually
	numbered rows.
	"""
	def __init__(self, **k):
		Grid.__init__(self, **k)
		self.__start = k.get('start', 1)
		self.__titles = k.get('titles')
		self.__tsep = k.pop('tsep', '')
		self.__sep = k.get('sep', '')
	
	
	def format(self, data, **k):
		i = k.get('start', self.__start)
		tsep = k.get('tsep', self.__tsep)
		title = k.get('titles', self.__titles)
		flist = []
		
		try:
			# maybe it's a dict
			jf = trix.ncreate('fmt.JCompact')
			for x in data.keys():
				flist.append([x+tsep, jf.format(data[x])])
		
		except Exception as ex:
			if title:
				for x in data:
					flist.append([title(i)+tsep, x])
					i += 1
			else:
					for x in data:
						flist.append([str(i)+tsep, x])
						i += 1
		
		return Grid.format(self, flist, **k)

