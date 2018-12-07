#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


import ast
from ..util.dq import *
from ..util.enchelp import *
from ..fmt.jformat import *
from ..fs.file import *


class JConfig(EncodingHelper):
	"""
	JConfig is a config-file manager that reads JSON or text files that 
	ast.literal_eval can parse.
	
	Once created, JConfig provides methods that let you navigate,
	display, edit, and eventually save the text representation of the
	config data structure as JSON.
	
	JConfig's nomenclature favor dict structures as the config type,
	but list-like structures can also be parsed and used as config.
	The naming of methods and properties, however, typically make more
	sense for dicts. 
	"""
	
	
	def __init__(self, path, default=None, **k):
		"""
		Pass config file path, an optional `default` config template, 
		and encoding-related keyword arguments. If the file specified
		by `path` does not exist, it will be created immediately. If
		the `default` argument is given, it's contents are coppied to
		the `path` immediately.
		
		NOTES:
		 * JSON is the default input format, but a file readable by 
		   `ast.literal_eval` may also be given as keyword arg `default`.
		   This provides an easy way to initialize a config file with
		   default contents.
		 * If `default` argument is given, its path points to an existing
		   file. The contents of the file (along with. any subsequent 
		   alterations) will replace any data in the file at `self.path` 
		   when the `self.save()` method is called.
		
		REMEMBER:
		 * The object loads both json and ast, but can only write JSON.
		 * The default file is never written to by this class.
		
		IMPORTANT:
		 * Be sure to pass affirm='touch' for new config files.
		 * If the file or default file is not utf8, pass it's encoding
		   as a keyword argument.
		"""
		
		k.setdefault('encoding', DEF_ENCODE)
		EncodingHelper.__init__(self, **k)
				
		# basic variables
		self.__object = None      # the parsed object
		self.__default = default  # path to `default` template
		self.__path = path        # path to json file
		
		#
		# Read and parse config file, coppied from a default, if the
		# "default" kwarg specified a path.
		#
		# NOTE: kwargs get passed to the load method only on the first
		#       call, here from the constructor. After this, the default,
		#       if it exists, will have been read and the config will
		#       have been read (in the given encoding) and written in 
		#       utf8-encoded bytes.
		# ALSO: The self.__load() method sets the self.obj property.
		#
		self.__load(**k)
		
		# start with selection object on self.__object
		self.__sel = self.__object
		
	
	# ---- file/path properties -----
	
	@property
	def default(self):
		"""Path to a default config template, or None."""
		return self.__default
	
	@property
	def path(self):
		"""File path to this config file."""
		return self.__path
	
	
	# ---- root object properties -----
	
	@property
	def obj(self):
		"""The object loaded from this config file."""
		return self.__object
	
	@property
	def config(self):
		"""Alias for `obj`; The object loaded from this config file."""
		return self.__object
	
	@property
	def type(self):
		"""Alias for `obj`; The object loaded from this config file."""
		return type(self.__object)
	
	@property
	def keys(self):
		"""
		Returns the list of the root config dict's keys (or, if the root
		config object is a list, the number	of items in that list).
		""" 
		try:
			return list(self.__object.keys())
		except:
			return len(self.__object)
	
	
	# ---- selection properties -----
	
	@property
	def sel(self):
		"""
		Reference an object within the self.config. See self.select().
		"""
		return self.__sel
	
	@property
	def selected(self):
		"""Alias for `self.sel` property"""
		return self.__sel
	
	@property
	def selkeys(self):
		"""Return the list of `self.selected` keys."""
		try:
			return self.__sel.keys()
		except:
			return len(self.__sel)
	
	
	
	# ---- selection maintenance -----
	def select(self, *a):
		"""
		Set the selection `self.selected` to the key given as the first 
		argument. 
		
		If no arguments are given, the selection is returned to the root
		object (the entire config file). 
		"""
		if len(a):
			for d in a:
				self.__sel = self.__sel[d]
		else:
			self.__sel = self.obj
	
	def deselect(self):
		"""Return selection to the root object."""
		self.__sel = self.obj
	
	
	def add(self, key, value):
		"""Add `value` to selected structure at `key`."""
		try:
			self.sel.insert(key, value) # works for list
		except AttributeError:
			self.sel[key] = value       # works for dict
	
	
	def set(self, key, value):
		"""Set `value` to selected structure at `key`."""
		self.sel[key] = value
	
	
	def rmv(self, key):
		"""Remove `key` from selected structure."""
		del(self.sel[key])
	
	
	
	# ---- re: files -----
	
	# SAVE
	def save(self, **k):
		"""Save the current self.obj to the json config file."""
		
		fmt = k.get('format', "display").lower()
		if fmt == 'display':
			conf = JDisplay().format(self.obj)
		elif fmt == 'compact':
			conf = JCompact().format(self.obj)
		elif fmt in ['json', None]:
			conf = JSON().format(self.obj)
		else:
			raise Exception('invalid-format-spec', xdata(
					use1=["display", 'compact', 'json', None]
				))
		
		# don't forget to actually save the file :-/
		f = trix.path(self.path).wrapper(**self.ek)
		f.write(conf)
	
	
	# RELOAD
	def reload(self):
		"""Reload the last saved version of the config file."""
		self.__load()
		
	
	
	
	#
	# MANIPULATION UTILS
	#
	
	# query/display
	def query(self, spec=None):
		"""
		Pass a list of nested keys (string) or offsets (int) leading to
		an object within self.obj. Pass None (or exclude argument) to
		reset selection to self.obj.
		
		NOTE: This method uses `util.dq` to retrieve objects within an
		      object. Always pass a list object as the `spec` argument.
		      Passing a delimited string will still work, but you will
		      probably, sooner or later, get unexpected results unless  
		      you *really* understand the "dirty version" of the dq 
		      class's path specification.
		"""
		return dq(self.obj, spec) if spec else self.obj
	
	def display(self, spec=None):
		"""Print this object to the terminal in JSON display format."""
		trix.display(self.query(spec))
	
	def show(self, spec=None):
		"""Like `display`, but on the selected (`self.sel`) data."""
		trix.display (dq(self.sel, spec) if spec else self.sel)
	
	
	
	#
	# LOAD (on init)
	#

	def __load(self, **k):
		
		TXT = None
		try:
			#
			# Full kwargs are passed the first time because a non-utf8
			# encoding may be supplied for the default file. On potential
			# subsequent calls (via `self.reload`) the file at self.path 
			# will be populated and will have been written in utf8, so 
			# there's no need for kwarg 'affirm' since the real target 
			# file already exists.
			#
			k = k or {'encoding':'utf_8'}
			
			# auto-affirm if default exists
			if self.default:
				k.setdefault('affirm', 'touch') 
			
			# 1 - read file at `self.path`
			TXT = Path(self.path, **k).reader(**k).read()
			
			# 2 - now there's a `path` file, but it may be empty
			if not TXT.strip():
				#
				# there's nothing in the config file...
				#
				
				# if there's no default file, return and empty dict
				if not self.default:
					outf = File(self.path, encoding="utf_8", affirm='touch')
					outf.write("{}")
					self.__object = {}
				
				else:
					#
					# If there *is* a default file, we have to be careful
					# since (despite that it can *read* ast) is only supposed
					# to write JSON. So...
					#
					
					# A) read the default file's contents.
					TXT = File(self.default, **k).read()
					
					#
					# B) Get the object and reformat as json so that only the 
					#    JSON content will be included, no comments, etc...
					#
					OBJ = self.__parse(TXT)
					TXT = trix.formatter(f='JDisplay').format(OBJ)
					
					# C) write the default config to the file
					outf = File(self.path, encoding="utf_8", affirm='touch')
					outf.write(TXT)
					
					# store the object in self.__object
					self.__object = OBJ
			
			#		
			# 3 - load json to the data object, `self.__object`
			# try with ast (in case loading a default given in ast).
			#
			else:
				self.__object = self.__parse(TXT)
		
		except FileNotFoundError as ex:
			raise type(ex)(xdata(
				path=self.path, affirm=k.get('affirm'),
				suggest="affirm='touch'"
			))
		
		except IsADirectoryError as ex:
			raise type(ex)(ex.args, xdata(
				k=k, txt=TXT, path=self.path, dfile=self.default
			))
	
	
	def __parse(self, txt):
		try:
			try:
				return ast.literal_eval(txt)
			except:
				# this should cause a exception that gives a line number
				compile(txt, self.path, 'eval')
				raise # if not, raise anyway
		
		except BaseException as ast_ex:
			# ast failed - try json
			try:
				return json.loads(txt)
			except BaseException as json_ex:
				raise Exception ("config-read-error", xdata(path=self.path, 
					json = {"type" : type(json_ex), "args" : json_ex.args},
					ast  = {"type" : type(ast_ex),  "args" : ast_ex.args}
				))

