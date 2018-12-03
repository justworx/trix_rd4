#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

import sys, time, traceback, json
try:
	import thread
except:
	import _thread as thread


#
# VERSION
#  - The official version of the `trix` package is currently
#    "Version: zero; rough draft four; under construction".
#
VERSION = 0.0000

#
# AUTO_DEBUG
#  - Controls the formatting of raised Exceptions.
#  - The trix package is very complex, making it really hard to
#    track down bugs. This formatting of exceptions really helps.
#  - If you want exceptions the old-fashioned way, set it False.
#
AUTO_DEBUG = True

#
# DEF_ENCODE
#  - The default encoding for the trix package is now determined by
#    sys.getdefaultencoding(). I don't know if that method can fail,
#    but if it does, 'utf_8' is used as a backup.
#  - This change is experimental. DEF_ENCODE used to be set directly
#    to 'utf_8'. I don't expect this to cause any problems, but in
#    the event it does, I'll switch back to a hard-coded default of
#    'utf_8'.
#
DEF_ENCODE = sys.getdefaultencoding() or 'utf_8'

#
# DEF_NEWL
#  - The default newline sequence.
#
DEF_NEWL = '\r\n'

#
# CONFIG / CACHE
#  - Default root directory for storage of config and cache files.
#  - These are the defaults for many *nix systems, and should work
#    for Windows. I'm hoping, though, that I'll learn of better
#    values for Windows before too much longer. 
#
DEF_CONFIG = "~/.config/trix"
DEF_CACHE  = "~/.cache/trix"

#
# DEFAULT INDENTATION
#  - Number of spaces to use when indenting formatted text, tab
#    replacement, etc...
#
DEF_INDENT = 2

#
# LOGLET FILE PATH/NAME
#
DEF_LOGLET = "./loglet"



#
# TRIX CLASS
#
class trix(object):
	"""Utility, debug, import; object, thread, and process creation."""
	
	__m  = __module__
	__mm = sys.modules
	
	Logging = 0 #-1=print; 0=None; 1=log-to-file
	
	
	# ---- object creation -----
	
	# INNER PATH	
	@classmethod
	def innerpath(cls, innerPath=None):
		"""
		Prefix `innerPath` with containing packages.
		
		Return a string path `innerPath` prefixed with any packages that
		contain this module. If the optional `innerPath` is None, the 
		path to (and including) this package is returned.
		
		>>> trix.innerpath("app.console")
		"""
		p = '.%s' % (innerPath) if innerPath else ''
		if cls.__m:
			return "%s%s" % (cls.__m, p)
		else:
			return innerPath
	
	
	# INNER F-PATH	
	@classmethod
	def innerfpath(cls, innerFPath=None):
		"""
		Return a file path from within the trix package.
		
		>>> trix.innerfpath('app/config/en.conf')
		"""
		ifp = cls.innerpath().split('.')
		if innerFPath:
			ifp.append(innerFPath)
		return "/".join(ifp)
	
	
	# MODULE
	@classmethod
	def module (cls, path):
		"""
		Returns a module given a string `path`. Specified module may be 
		external to the trix package. 
		
		>>> trix.nmodule('socket')
		"""
		try:
			return cls.__mm[path]
		except KeyError:
			__import__(path)
			return cls.__mm[path]
	
	
	# N-MODULE
	@classmethod
	def nmodule(cls, innerPath):
		"""
		Like `module`, but pass the inner path instead of full path.
		
		>>> trix.nmodule('fs.dir')
		"""
		return cls.module(cls.innerpath(innerPath))
	
	
	# CREATE
	@classmethod
	def create(cls, modpath, *a, **k):
		"""
		Create and return an object specified by argument `modpath`. 
		
		The dot-separated path must start with the path to the desired
		module. It must be suffixed with a name of a class defined in the
		specified module. (Eg, 'package.subpackage.module.ClassName')
		
		Any additional arguments and keyword args will be passed to the
		class's constructor.
		
		>>> sock = trix.create("socket.socket")
		"""
		p = modpath.split(".")
		m = p[:-1] # module
		o = p[-1]  # object
		
		try:
			if m:
				mm = cls.module(".".join(m))
				T  = mm.__dict__[o]
			else:
				T = __builtins__[o]
		
		except KeyError:
			raise KeyError('create-fail', xdata(path=modpath,
					mod=".".join(m), obj=o
				))
		
		try:
			return T(*a, **k)
		except BaseException as ex:
			raise type(ex)(xdata(path=modpath, a=a, k=k, obj=o))
		
	
	# N-CREATE - create an object given path from inside trix
	@classmethod
	def ncreate(cls, innerPath, *a, **k):
		"""
		Create and return an object specified by argument `innerPath`.
		The dot-separated path must start with the path to the desired
		module *within* this package (but NOT prefixed with the name of
		this package. It must be prefixed with a name of a class defined
		in the specified module. Eg, 'subpackage.theModule.TheClass
		
		Any additional arguments and keyword args will be passed to the
		class's constructor.
		
		USE: The ncreate() method is used from within this package. For 
		     normal (external) use, use the create() method.
		
		>>> trix.ncreate("app.console.Console")
		"""
		a = a or []
		k = k or {}
		return cls.create(cls.innerpath(innerPath), *a, **k)
	
	
	# VALUE - return a value (by name) from a module
	@classmethod
	def value(cls, pathname, *args, **kwargs):
		"""
		Returns an object as specified by `pathname` and additional args.
		
		Returns a module, class, function, or value, as specified by the
		string argument `pathname`. If additional *args are appended, 
		they must name a class, method, function, or value defined within 
		the object specified by first argument. A tupel is returned.
		
		>>> trix.value('socket',"AF_INET","SOCK_STREAM")
		"""
		
		try:
			return __builtins__[pathname](*args, **kwargs)
		except:
			pass
		
		try:
			mm = mc = cls.module(pathname)
		except:
			# If `pathname` points to a module or function, split it and 
			# load its containing module.
			pe = pathname.split('.')
			
			# only pop the last item if there's more than one element
			nm = pe.pop() if len(pe) > 1 else None
			
			# get the module
			mm = cls.module('.'.join(pe))
			
			# Get the last object specified by `pathname`; This object must
			# be either a module or a class, not a function or other value.
			# If no other args are specified, this is the final result.
			mc = mm.__dict__[nm] if nm else mm
		
		# If there are no *args, return the last [module or class] object
		# specified by `pathname`.
		if not args:
			return mc
		
		# if args are specified, forget about the mod/cls item and just
		# return any requested values from it.
		rr = []
		for v in args:
			try:
				rr.append(mc.__dict__[v])
			except KeyError:
				if 'default' in kwargs:
					return kwargs['default']
				return ()
			except NameError:
				# TO DO:
				# Make this work when `v` is a module. It does work if the
				# module `v` would specify is already loaded, but not if it's
				# not... which is inconsistent... which bothers me.
				raise
		
		# If one *args value was specified, return it. If more than one
		# was specified, return them as a tuple.
		if len(rr) == 1:
			return rr[0]
		return tuple(rr)
	
	
	# N-VALUE
	@classmethod
	def nvalue(cls, pathname, *a, **k):
		"""
		Like `value`, but pass the inner path instead of full path.
		
		>>> trix.nvalue("util.compenc.b64")
		"""
		try:
			return cls.value(cls.innerpath(pathname), *a, **k)
		except KeyError as kex:
			try:
				return __builtins__[pathname]
			except Exception as ex:
				raise type(ex)(ex.args, 'err-nvalue-fail', xdata(
						pathname=pathname
					))
	
	
	# PATH
	@classmethod
	def path(cls, path=None, *a, **k):
		"""
		Return an fs.Path object at `path`.
		
		>>> p = trix.path().path
		>>> trix.path().dir().ls()
		>>> trix.path("trix/app/config/app.conf").reader().readline()
		"""
		try:
			return cls.__FPath(path, *a, **k)
		except:
			# requires full module path, so pass through innerpath()
			cls.__FPath = cls.module(cls.innerpath('fs')).Path
			return cls.__FPath(path, *a, **k)
	
	# N-PATH
	@classmethod
	def npath(cls, innerFPath=None, *a, **k):
		"""
		Return an fs.Path for a file-system object within the trix 
		directory.
		
		>>> e = 'UTF_8'
		>>> r = trix.npath("app/config/app.conf").reader(encoding=e)
		>>> r.readline()
		"""
		return cls.path(cls.innerfpath(innerFPath), *a, **k)
	
	
	# CONFIG
	@classmethod
	def config(cls, config=None, **k):
		"""
		If `config` is given as a dict, the dict is updated with any 
		given keyword arguments and returned.
		
		If `config` is the path to a JSON or ast-parsable text file, the
		file is parsed and the resulting structure is returned. In this
		case, any keyword args are passed to the JConfig constructor.
		
		>>> trix.config("trix/app/config/app.conf")
		>>> trix.config(None, x=9)
		>>> trix.config(y='x')
		>>> trix.config({'y':'x'}, y="X") # kwargs replace dict keys
		>>> trix.config()
		"""
		if config == None:
			return dict(k)
		try:
			# by dict 
			config.update(**k)
		except AttributeError:
			# by path...
			jconf = cls.jconfig(config, **k)
			config = jconf.obj
		return config
	
	
	# N-CONFIG
	@classmethod
	def nconfig(cls, config=None, **k):
		"""
		Same as `trix.config`, but file paths must be given as partial
		paths starting within the trix package directory.
		
		>>> # See trix.config, above, for more usage examples.
		>>> trix.nconfig("app/config/app.conf")
		"""
		if config == None:
			return dict(k)
		if isinstance(config, dict):
			config.update(k)
			return config
		return cls.config(trix.innerfpath(config), **k)
	
	
	# PROCESS
	@classmethod
	def process(cls, path, *a, **k):
		"""
		Pass a class `path` and any needed args/kwargs. A Process object
		is returned. Call the Process object's `launch` method passing a
		method name (string) and any additional args/kwargs (or no params,
		if the class constructor starts processing).
		
		>>> p = trix.process("trix.net.server.Server", 9999)
		>>> p.launch('run')
		>>> c = trix.create("trix.net.connect.Connect", 9999)
		>>> c.write("Test")
		>>> c.read()
		>>> p.stop() # end the remote process
		"""
		# REM! `path` is the module.class to launch within the `Process`.
		return cls.ncreate("util.process.Process", path, *a, **k)
	
	
	# N-PROCESS
	@classmethod
	def nprocess(cls, innerPath, *a, **k):
		"""
		Like `process`, but given remote object's `innerPath`.
		
		>>> p = trix.nprocess("net.server.Server", 9999).launch('run')
		>>> c = trix.create("trix.net.connect.Connect", 9999)
		>>> c.write("Test")
		>>> c.read()
		>>> p.stop() # end the remote process
		"""
		#
		# The `innerPath` arg is expanded to be the full module.class 
		# path that will be launched by `cls.process()`.
		#
		return cls.process(cls.innerpath(innerPath), *a, **k)
	
	
	# ---- process/thread creation -----
	
	# PID
	@classmethod
	def pid(cls):
		"""
		Return the id for this process.
		
		>>> trix.pid()
		"""
		try:
			return cls.__pid
		except:
			import os
			cls.__pid = os.getpid()
			return cls.__pid
	
	
	# POPEN
	@classmethod
	def popen (cls, *a, **k):
		"""
		Open a subprocess and return a Popen object created with the given
		args and kwargs. This functions exactly as would calling the popen
		function directly, except that stdout and stderr are enabled by 
		default.
		
		The return value is a Popen object. Use its communicate() method
		to read results of the command.
		
		KWARGS REFERENCE:
		bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, 
		preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None,
		universal_newlines=False, startupinfo=None, creationflags=0
		
		>>> trix.popen("dir").communicate()
		"""
		try:
			m = cls.__sp
		except:
			m = cls.__sp = cls.module("subprocess")
		
		# set defaults and run the process
		k.setdefault("stdout", m.PIPE)
		k.setdefault("stderr", m.PIPE)
		return m.Popen(*a, **k)
	
	
	# START - Start new thread 
	@classmethod
	def start (cls, x, *a, **k):
		"""
		Start callable object `x` in a new thread, passing any given 
		*args and **kwargs.
		
		>>> def test(): print("Testing 1 2 3");
		>>> trix.start(test)
		"""
		try:
			thread.start_new_thread(x, a, k)
		except:
			pass
	
	
	
	# ---- general -----
	
	# PROXIFY
	@classmethod
	def proxify(cls, obj):
		"""
		Return a proxy for `obj`. If `obj` is already a proxy, returns
		the proxy `obj` itself.
		
		>>> def test(): print("Testing 1 2 3");
		>>> prxy = trix.proxify(test)
		>>> prxy()
		>>> trix.proxify(prxy)
		"""
		try:
			return cls.create('weakref.proxy', obj)
		except BaseException:
			return obj
	
	
	# J-PARSE
	@classmethod
	def jparse(cls, jsonstr, **k):
		"""
		Parse json to object.
		
		>>> trix.jparse('{"a": 1, "b": 9, "c": 4}')
		"""
		try:
			return json.loads(jsonstr)
		except TypeError:
			k.setdefault('encoding', DEF_ENCODE)
			return json.loads(jsonstr.decode(**k))
	
	
	# J-CONFIG
	@classmethod
	def jconfig(cls, filepath, **k):
		"""
		Pass string `filepath` to a JSON (or ast-parsable) config file. 
		Optional `default` kwarg identies file path containing default 
		contents for a new config file in case no file exists at 
		`filepath`. Use `ndefault` kwarg instead for the internal path
		(within the trix directory) to a default file.
		
		An `app.JConfig` object is returned.
		
		NOTES:
		 * The default path should point to a static default config file
		   (in ast or json format).
		 * If default path is given, affirm defaults to "touch".
		 * Be careful that your default filepath is not unintentionally
		   set to the same path as the `filepath` argument, or your
		   original default file may be overwritten.
		
		>>> jc = trix.jconfig("trix/app/config/app.conf")
		>>> print (jc.config)
		"""
		default = k.get('default', cls.npath(k.get('ndefault')).path)
		k['default'] = default
		
		#trix.display({"trix-DEFAULT:":default,'filepath':filepath,'k':k})
		
		# This should protect against most (if not all) unintentional
		# overwriting of the default file.
		if default and (default == filepath):
			raise ValueError("Matching target and default paths.", xdata(
					default=default, filepath=filepath, k=k
				))
		m = cls.nmodule("app.jconfig")
		return m.JConfig(filepath, **k)
	
	
	# K-COPY
	@classmethod
	def kcopy(cls, d, keys):
		"""
		Copy `keys` from `d`; return in a new dict.
		
		Creates a subset of dict keys in order to select only desired (or 
		allowed) keyword args before passing to functions and methods. 
		Argument `keys` may be passed as a space-separated string, but 
		this won't work in all situations. It's much safer to pass the 
		`keys` as a list object.
		
		The original dict is never altered by `kcopy`.
		
		>>> d = dict(a=1, b=9, c=4)
		>>> trix.kcopy(d, "b")
		>>> trix.kcopy(d, ['a', 'c'])
		>>> d
		"""
		try:
			keys=keys.split()
		except:
			pass
		return dict([[k,d[k]] for k in keys if k in d])
	
	
	# K-POP
	@classmethod
	def kpop(cls, d, keys):
		"""
		Remove and return a set of `keys` from given dict. Missing keys 
		are ignored.
		
		Argument `keys` may be passed as a space-separated string, but 
		this won't work in all situations. It's much safer to pass the 
		`keys` as a list object.
		
		NOTE: The dict `d` that you pass to this method is affected.
		      Specified keys will be removed and returned in a separate
		      dict.
		
		>>> d = dict(a=1, b=9, c=4)
		>>> x = trix.kpop(d, "b")
		>>> print (x, d)
		"""
		try:
			keys=keys.split()
		except AttributeError:
			pass
		r = {}
		for k in keys:
			if k in d:
				r[k] = d[k]
				del(d[k])
		return r
	
	
	
	# ---- display/debug -----
	
	# DEBUG
	@classmethod
	def debug(cls, debug=True, showtb=True):
		"""
		Enable/disable debugging/traceback. This should pretty much be
		left alone. The trix code is too convoluted to debug without it.
		However, it's available if you want to turn it off. If debug is
		set to False, normal python excpetion format is displayed (and
		tracebacks won't be duplicated). When `debug` is on but `showtb`
		is False, the extended exception format is still shown but the
		trailing traceback is ignored.
		"""
		Debug.debug(debug,showtb)
	
	
	# FORMATTER (default, JDisplay)
	@classmethod
	def formatter(cls, *a, **k):
		"""
		Return a fmt.FormatBase subclass described by keyword "f" (with
		"f" defaulting to "JDisplay"). Args and Kwargs are dependent on
		the "f" format value. See trix.fmt.* class doc to learn more 
		about how to control formats for various FormatBase subclasses.
		
		Call the returned object's `output` to display the output; Call 
		the `format` method to return a str value containing formatted 
		output.
		
		>>> j = trix.formatter(f="JCompact")
		>>> j.output(dict(a=1,b=9,c=4))
		>>>
		>>> f = trix.formatter(f="Lines")
		>>> f.format("Hello!", ff="title")
		>>> f.output("Hello!", ff="title")
		"""
		f = k.pop("f", "JDisplay")
		return cls.ncreate("fmt.%s"%f, *a, **k)
	
	
	# DISPLAY - Util. JSON is the main data format within the package.
	@classmethod
	def display(cls, data, *a, **k):
		"""
		Print python data (dict, list, etc...) in, by default, display 
		format. See `trix.formatter()` and various trix.fmt package doc
		for details on required and optional args/kwargs. 
		
		>>> trix.display({'a':1, 'b':9, 'c':4})
		"""
		cls.formatter(*a, **k).output(data)

	
	# TRACE-BK
	@classmethod
	def tracebk(cls):
		"""Return current exception's traceback as a list."""
		tb = sys.exc_info()[2]
		if tb:
			try:
				return list(traceback.extract_tb(tb))
			finally:
				del(tb)
	
	
	# X-DATA
	@classmethod
	def xdata(cls, data=None, **k):
		"""
		Package extensive exception data into a dict. This is a utility
		for the trix package; it helps generate extensive exception data
		for use by the debug handler. That doesn't mean it's not still
		useful for other purposes.
		
		>>> xdata(a=1, b=9, c=4)
		"""
		return xdata(cls, data, **k)
	
	
	
	# ---- LOGGING -----
	
	# LOG
	@classmethod
	def log(cls, *a, **k):
		"""
		Returns Loglet for this process. Pass args/kwargs to log. The
		trix.Logging class variable determines the output:
		
		 * 1  = Log to file
		 * 0  = Logging turned off (the default)
		 * -1 = Print log entries to the terminal
		
		Calling this method with trix.Logging set to 1 generates a log 
		file named for the process ID. This is helpful for debugging 
		multi-process situations.
		
		#
		# Check your working directory for log files after this example!
		# They can really fill up a directory quickly if you forget.
		#
		>>> trixc = trix.trixc()
		>>> dbg = trixc.Logging
		>>> trixc.Logging = 1
		>>> trixc.log('a', 'b', 'c', x=1)
		>>> trixc.Logging = dbg
		
		#
		# NOTE: 
		#  - The `trix.trixc()` method is necessary here because this 
		#    example must get and set the trix.Logging class variable,
		#    while `trix` may refer either to the trix class or the trix
		#    module.
		#    
		#    While this may seem a silly distinction, it serves to make
		#    this example work regardless of how you imported trix.
		#    
		#    One of the primary goals of the trix project is ease of use
		#    from the python interpreter. With `trix.trixc()`, we need
		#    never suffer an error because we typed `import trix` rather
		#    than `from trix import *` (or vice-versa).
		#
		"""
		if cls.Logging < 0:
			with thread.allocate_lock():
				a = list(a)
				a.append(k)
				cls.display(a)
		elif cls.Logging > 0:
			with thread.allocate_lock():
				try:
					cls.__log(*a, **k)
				except:
					cls.__log = cls.ncreate('util.loglet.Loglet', cls.__m)
					cls.__log(*a, **k)
	
	
	@classmethod
	def trixc(cls):
		"""
		Returns the trix class.
		
		This may be necessary when scripting outside the library in a 
		situation where you don't know whether the trix library was 
		imported as "import trix" or "from trix import *".
		"""
		return cls
	
	
	
	# --------- new - experimental ---------
	
	@classmethod
	def signals(cls):
		"""Manage the handling of signals. See trix.util.signals."""
		try:
			return cls.__signals
		except:
			cls.__signals = trix.nvalue("util.signals.Signals")
			return cls.__signals



#
# CONVENIENCE
#
config     = trix.config
create     = trix.create
debug      = trix.debug
display    = trix.display
innerpath  = trix.innerpath
innerfpath = trix.innerfpath
formatter  = trix.formatter
jconfig    = trix.jconfig
jparse     = trix.jparse
kcopy      = trix.kcopy
kpop       = trix.kpop
log        = trix.log
module     = trix.module
nconfig    = trix.nconfig
ncreate    = trix.ncreate
nmodule    = trix.nmodule
nprocess   = trix.nprocess
nvalue     = trix.nvalue
path       = trix.path
npath      = trix.npath
pid        = trix.pid
popen      = trix.popen
process    = trix.process
proxify    = trix.proxify
signals    = trix.signals
start      = trix.start
tracebk    = trix.tracebk
trixc      = trix.trixc
value      = trix.value



#
# LOADER (and NLoader)
#


class Loader(object):
	"""Intended for internal use."""
	
	def __init__(self, module, value=None, loader=trix.module):
		#
		#Pass module name (string) and function name (string). Loading of
		#module is deferred until the first call.
		#
		self.__L = loader
		self.__M = module
		self.__V = value
	
	def __repr__(self):
		T = type(self)
		aa = (
			T.__name__, self.__L.__name__, self.__M, repr(self.__V)
		)
		return "<%s trix.%s('%s', %s)>" % aa
	
	@property
	def module(self):
		# Return the module object as specified to construcor.
		try:
			return self.__module
		except AttributeError:
			self.__module = self.__L(self.__M) # use loader
			return self.__module
	
	@property
	def value(self):
		# Return the value specified to construcor.
		try:
			return self.__value
		except AttributeError:
			self.__value = self.module.__dict__[self.__V]
			return self.__value

	def __call__(self, *a, **k):
		# Load the specified method/function and return its result.
		self.__call__ = self.value
		return self.__call__(*a, **k)

	def __getitem__(self, x):
		# Get any member (function, value, etc...) from the module.
		return self.module.__dict__[x]


# N-LOADER
class NLoader(Loader):
	"""Intended for internal use."""
	def __init__(self, module, value=None):
		# Init loader with the trix.nmodule loader."""
		Loader.__init__(self, module, value, loader=trix.nmodule)


#
# COMPATABILITY
#

# common python 2/3 typedefs
try:
	basestring
except:
	#
	# The following are defined if basestring is undefined (before 
	# python 2.3, and for python 3 and higher). These values make the
	# important distinction between unicode and byte values/strings.
	# These designations are important in some rare cases.
	#
	basestring = unicode = str
	unichr = chr
	
	# Convence for development.
	if AUTO_DEBUG:
		try:
			try:
				from importlib import reload
			except:
				from imp import reload
		except:
			pass



#
# For implementations with unicode support compiled without wide 
# character support, this allows comparison of wide characters. 
# This should solve many problems on pre-python3 Windows systems.
#
try:
	unichr(0x10FFFF) # check wide support
except:
	import struct
	def unichr (i):
		return struct.pack('i', i).decode('utf-32')



#
# This supports python versions before 2.6 when the bytes type was 
# introduced.
#
try:
	bytes
except:
	# this only happens pre-version 2.6
	bytes = str



#
# EXTENDED DEBUGGING
#  - This package provides extensive debugging information in raised
#    exceptions, so a little extra formatting is needed to help make
#    sense of some of the things that might go wrong.
#
class xdata(dict):
	"""Package extensive exception data into a dict."""

	def __init__(self, data=None, **k):

		# argument management
		data = data or {}
		data.update(k)

		# create and populate the return dict
		self['xdata'] = data
		self.setdefault('xtime', time.time())

		# If this is a current exception situation,
		# record its values
		try:
			tblist = None
			xtype, xval = sys.exc_info()[:2]
			tblist = trix.tracebk()
			if xtype or xval or tblist:
				self['xtype'] = xtype
				self.__xtype  = xtype
				self['xargs'] = xval.args
				if tblist:
					self['xtracebk'] = list(tblist)
		finally:
			if tblist:
				del(tblist)
				tblist = None



#
# DEBUG HOOK
#
def debug_hook(t, v, tb):
	
	with thread.allocate_lock():

		# catch errors in the debug hook and disable debugger
		try:
			
			# KEYBOARD ERROR
			if isinstance(v, KeyboardInterrupt):
				print ("\n", t, "\n\n")

			else:
				print (t)

				# SYNTAX ERROR
				if isinstance(v, SyntaxError):
					print(" ->", str(type(v)))

				#
				# DISPLAY ARGS
				#
				if v.args:
					try:
						trix.display(list(v.args), sort_keys=1)
					except Exception:
						args = [str(a) for a in v.args]
						print ("[")
						if len(v.args)==1:
							print (" ", str(v.args))
						else:
							for a in v.args:
								try:
									print("  %s" % str(a))
								except:
									print ("  ", a)
						print ("]")

				#
				# TRACEBACK
				#  - show traceback, if enabled
				#
				if tb and Debug.showtb():
					print ("Traceback:")
					traceback.print_tb(tb)
				print ('')
		
		#
		# EXCEPTION IN EXCEPTION HANDLER
		#
		except BaseException:
			print ("\n#\n# DEBUG HOOK FAILED!")
			try:
				xxtype, xxval = sys.exc_info()[:2]
				print ("# - Debug Hook Err: %s %s\n#" % (xxtype, str(xxval)))
			except:
				pass
			
			# turn off debugging and re-raise the exception
			debug(False)
			print ("# - Debug Hook is Disabled.")
			raise
		finally:
			if tb:
				del(tb)
				tb = None


#
# DEBUG
#
class Debug(object):
	__DEBUG = False
	__TRACE = False
	__SYSEX = sys.excepthook
	
	@classmethod
	def debug(cls, debug=True, showtb=False, **k):
		cls.__DEBUG = bool(debug)
		cls.__TRACE = bool(showtb)
		if cls.__DEBUG:
			sys.excepthook = debug_hook
		else:
			sys.excepthook = cls.__SYSEX
	
	@classmethod
	def debugging(cls):
		return cls.__DEBUG
	
	@classmethod
	def showtb(cls):
		return cls.__TRACE



if AUTO_DEBUG:
	Debug.debug(1,1)

