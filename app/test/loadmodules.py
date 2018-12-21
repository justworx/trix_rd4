#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ... import *


def report(**k):
	"""
	Run basic compilation test.
	
	Loads all modules and prints a report listing modules and a brief
	error message, if any.
	"""
	Test(**k).report()
	#trix.ncreate('app.test.test_url.report')
	


#
# TEST - LOAD ALL MODULES
#
class Test(object):
	def __init__(self, **k):
		
		self.debug = k.get('debug', False)
		
		# the directory holding the root package (eg, ~/dev, ~, etc...)
		self.parent = trix.path().path
		self.parlen = len(self.parent.split('/'))
		
		# the start of the import path (eg, dev.trix, dev.trix)
		self.inpath = trix.innerpath()
		
		# path elements within root package (eg, ['dev','trix'], etc...)
		inpathlist = self.inpath.split('.')
		
		# the name of this package
		self.package = inpathlist[-1]
		
		# path within the root package (eg, dev/trix, dev/trix)
		self.pkgpath = "/".join(inpathlist)
		
		# path to the package being tested (eg, trix, trix)
		self.path = "%s/%s" % (self.parent, self.pkgpath)
		
		# a Dir object to path containing *.py files to test
		self.dir = trix.ncreate('fs.dir.Dir', self.path)
		
		# CURRENTLY LOADED MODULES
		self.__loaded = {}
	
	
	
	#
	# RESULT STORAGE
	#
	
	@property
	def current(self):
		return self.__loaded
	
	
	#
	# MODULE PATHS - eg., "./trix/fs/dir.py"
	#
	
	@property
	def paths(self):
		"""Return list of *.py paths within package."""
		try:
			return self.__paths
		except:
			self.__paths = sorted(self.dir.find("*.py"))
			return self.__paths
	
	
	def pathgen(self):
		"""Generator for module (/full/dir/*.py) paths."""
		for path in self.paths:
			#print (" - ", path)
			if ('/bu/' in path) or (".bu" in path):
				pass
			elif '/x/' in path:
				pass
			elif '_x' in path:
				pass
			elif 'x_' in path:
				pass
			else:
				yield path
	
	
	#
	# MODULE SPEC - eg., "trix.fs.dir"
	#
	
	@property
	def modules(self):
		"""Return list of module (python.import.path) sepcifications"""
		try:
			return self.__modules
		except:
			self.__modules = sorted(self.modgen())
			return self.__modules
			
	
	def modgen(self):
		"""Generator for module (python-import) paths."""
		plen = self.parlen
		for path in iter(self.pathgen()): #self.paths:
			# path from within parent directory
			r = path.split('/')
			r = r[plen:] 
			
			# ignore files that start with x_
			if r[-1][:2]=='x_':
				continue
			
			# ignore init files, import their package path
			if r[-1] == '__init__.py': 
				r = r[:-1]
			
			# don't test __main__.py
			elif r[-1] != '__main__.py':
				
				# drop the .py where found at the end of module paths
				r[-1] = r[-1].split('.')[0]
				
				# yield the module name!
				p = '.'.join(r)
				
				# don't test a tester!
				if self.__module__ != r:
					yield p
	
	
	#
	# MODULE LOADING
	#
	
	def loadmodule(self, modspec):
		"""Import the module specified by `modspec`."""
		
		L = locals()
		G = globals()

		try:
			# for root module
			if modspec:
				m = __import__(modspec,G,L,[],0)
				
			# import (or reload) the modspec module
			elif modspec in self.__loaded:
				m = reload(self.__loaded[modspec])
			else:
				m = __import__(modspec,G,L,[],0)
			
			# store result
			self.__loaded[modspec] = dict(modspec=modspec, module=m)
			
		except BaseException as ex:
			self.__loaded[modspec] = dict(modspec=modspec, module=None, 
				error=xdata()
			)
			if self.debug:
				print ("modspec = %s" % modspec)
				raise
	
	
	
	def load(self):
		for modspec in self.modules:
			self.loadmodule(modspec)
	
	
	
	def report(self):
		if not len(self.current):
			self.load()
		
		gg = [["MODULE:", 'RESULT:']]
		for modspec in self.current:
			item = self.current[modspec]
			gg.append([
				modspec, "OK" if item.get('module') else "ERR! %s" % (
					str(item.get('error',{}).get('prior',{}).get('xargs', '?'))
				)
			])
		
		grid = trix.ncreate('fmt.grid.Grid')
		grid.output(sorted(gg))
