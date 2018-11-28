#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *
import os, glob


class Dir(Path):
	"""Directory functionality."""
	
	def __init__(self, path=None, **k):
		"""
		Pass an optional file system path. Default is '.'. Kwargs apply 
		as to Path.expand().
		"""
		p = k.get('dir', path)
		if not 'affirm' in k:
			k['affirm'] = 'checkdir'
		try:
			Path.__init__(self, p, **k)
		except Exception:
			raise ValueError('fs-invalid-dir', xdata(path=p)) 
		
		# requires py 2.6+
		self._walk = os.walk
	
	
	# CALL
	def __call__(self, item):
		"""
		Calling a Path object as a function returns a new Path object that
		points to its path "merged" with the (required) given `item`.
		
		For `Dir` objects, the given `item` may also be the integer offset
		into the directory listing.
		"""
		try:
			# this works if item is an integer index into this directory
			return Path.__call__(self, self[item])
		except TypeError:
			# this works if item is a string path
			return Path.__call__(self, item)
	
	
	def __getitem__(self, key):
		"""
		Dir objects can act as lists of the full path to the items inside
		the directory to which they point; Dir()[0] returns the full path
		to the first item in its directory listing.
		"""
		ls = self.ls()
		return self.merge(ls[key])
	
	# Path-only methods
	def cd(self, path):
		"""Change directory the given path."""
		p = self.merge(path)
		if not os.path.isdir(p):
			raise Exception ('fs-not-a-dir', xdata(path=p))
		self.path = p
	
	
	def ls(self, path=None):
		"""List directory at path."""
		return os.listdir(self.merge(path))
	
	"""
	#
	# THIS SECTION NEEDS SOME WORK
	#  - It may need to be moved to Path..
	#  - It needs thorough testing.
	#
	# Single file operations, path relative to this directory.
	#
	
	def head(self, path, lines=12, **k):
		# get the path to `path` relative to this directory
		p = Path(self.merge(path))
		
		# get a reader for that file
		r = p.reader(**k)
		
		# iterate, collecting `lines` results
		rr = []
		for line in r.lines:
			rr.append(line.strip())
			lines -= 1
			if lines < 1:
				break
		return rr
	
	def read(self, path, **k):
		return self.file(path).read(**k)
	
	def file(self, path, **k):
		return trix.ncreate('fs.file.File', self.merge(path), **k)
	"""
	
	
	#
	# Directory contents actions
	#
	
	def mkdir(self, path, *a):
		"""
		Create a directory described by path. If appended, additional 
		argument (mode) is passed on to os.makedirs().
		"""
		os.makedirs(self.merge(path), *a)

	def mv(self, pattern, dst):
		"""Move pattern matches to dst."""
		for src in self.match(pattern):
			shutil.move(src, self.merge(dst))
	
	# This needs to be tested thoroughly.
	#def cp(self, pattern, dst):
	#	#Move pattern matches to dst.
	#	for src in self.match(pattern):
	#		shutil.move(src, self.merge(dst))
	
	def rm(self, pattern):
		"""Remove files matching pattern."""
		for px in self.match(pattern):
			if os.path.isdir(px):
				shutil.rmtree(px)
			else:
				os.remove(px)
	
	
	#
	# Pattern Searching - Match, Find
	#
	
	def match(self, pattern):
		"""Return matching directory items for the given pattern."""
		return glob.glob(self.merge(pattern))
	
	
	def search(self, path, pattern=None, **k):
		"""
		REQUIRES: Python 2.6+
		
		Search directories recursively starting at the given `path`; 
		return list of all paths unless argument `pattern` is specified.
		
		KEYWORD ARGUMENT:
		If `fn` keyword is specified, its value must be callable; this 
		callable will be called once for each result path. If args 
		keyword exists, it must be an array of values to be passed as 
		individual additional arguments to fn.
		
		WARNING: There is no 'confirm' or 'undo' when passing a 'fn'.     
				     ALWAYS CHECK the search results *without a function* 
				     BEFORE using it with a function.
		
		This class makes minimal use of the os.walk function, which became
		available in python 2.6.
		"""
		if not pattern:
			raise ValueError('fs-pattern-required', xdata())
		path = self.merge(path)
		rlist = []
		
		# d = current dir path; dd = contained dir; ff = contained file;
		for d, dd, ff in self._walk(path):
			rlist.extend(self.match(os.path.join(d, pattern)))
		if 'fn' in k:
			fn = k['fn']
			for fpath in rlist:
				rr = {}
				aa = k.get('args', [])
				fn(fpath, *aa)
		else:
			return rlist
	
	
	def find(self, pattern, **k):
		"""
		REQUIRES: Python 2.6+
		
		Calls the .search() method passing this object's path and the 
		given `pattern` and keyword args. Read the search method help for
		more information.
		
		WARNING: There is no 'confirm' or 'undo' when passing a 'fn'.     
				     ALWAYS CHECK the find results *without a function* 
				     BEFORE using it with a function.
		"""
		return self.search(self.path, pattern, **k)
	
	
	
	
	
	#
	# EXPERIMENTAL. CONVENIENCE.
	#  - undocumented
	#  - displays dir listings
	#
	
	def li(self):
		"""Display items in grid."""
		trix.display(self.ls(), f='List')
	
	def list(self):
		"""Display items with detail."""
		
		rr = [["NAME", 'TYPE', "SIZE"]]   # <-------------- english words
		for p in self.ls():
			pp = Path(self.merge(p))
			try:
				stat = pp.stat()
				#print ('dir.list', pp, stat.st_size)
				size = stat.st_size
			except Exception as ex:
				size = ''
			rr.append([pp.name, pp.pathtype, size])
		
		# show output
		trix.display(rr, f="Grid")
	

