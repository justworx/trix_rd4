#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util import mime
from ..util.enchelp import *
import shutil, os, os.path as ospath

class Path(object):
	"""Represents a file system path."""
	
	# INIT
	def __init__(self, path=None, **k):
		"""
		Represents `path` given as string, or current working directory. 
		Pass kwargs as to the expand() method.
		"""
		self.sep = os.sep
		self.__p = self.expand(k.get('path', path or '.'), **k)
		try:
			self.__n = ospath.normpath(self.__p).split(self.sep)[-1]
		except TypeError:
			if isinstance(self.sep, unicode):
				self.sep = self.sep.encode()
			else:
				self.sep = self.sep.decode()
			self.__n = ospath.normpath(self.__p).split(self.sep)[-1]
			
			
	
	# CALL
	def __call__(self, path):
		"""
		Returns a new Path object representing this path "merged" with the
		(required) given `path`.
		"""
		return Path(self.merge(path))
	
	# REPR
	def __repr__(self):
		return str(type(self))
	
	# STR
	def __str__(self):
		"""The path as a string."""
		return self.path
	
	# UNICODE
	def __unicode__(self):
		"""The path as a unicode string (python 2 support)"""
		return unicode(self.path)
	
	# ENTER/EXIT
	def __enter__(self):
		return self
	
	def __exit__(self, *args):
		pass
	
	
	# PROPERTIES
	
	@property
	def mime(self):
		"""Return a Mime object for this object's path."""
		return trix.ncreate('util.mime.Mime', self.path)
	
	@property
	def parent(self):
		"""Return the path to this path's parent directory."""
		return ospath.dirname(self.path)
	
	@property
	def name(self):
		"""Return current path's last element."""
		return self.__n
	
	@property
	def path(self):
		"""Return or set this path."""
		return self.getpath()
	
	@path.setter
	def path(self, path):
		self.setpath(path)
	
	@property
	def pathtype(self):
		"""Return or set this path."""
		if self.isdir():
			return 'd'
		elif self.isfile():
			return 'f'
		elif self.islink():
			return 'l'
		elif self.ismount():
			return 'm'
		else:
			return "?"
	
	
	# METHODS
	
	def exists(self, path=None):
		"""True if path exists."""
		return ospath.exists(self.merge(path))
	
	def getpath(self):
		"""Return this object's path."""
		return self.__p
	
	def setpath(self, path):
		"""Set this object's path."""
		self.__p = path
		self.__n = ospath.normpath(path).split(self.sep)[-1]
	
	def isfile(self, path=None):
		"""True if path is a file."""
		return ospath.isfile(self.merge(path))
	
	def isdir(self, path=None):
		"""True if path is a directory."""
		return ospath.isdir(self.merge(path))
	
	def islink(self, path=None):
		"""True if path is a symbolic link."""
		return ospath.islink(self.merge(path))
	
	def ismount(self, path=None):
		"""True if path is a mount point."""
		return ospath.ismount(self.merge(path))
	
	def touch(self, path=None, times=None):
		"""Touch file at path. Arg times applies to os.utime()."""
		p = self.merge(path)
		try:
			with self.wrapper(p) as w:
				w.touch(times)
		except:
			with open(p, 'a'):
				os.utime(p, times)
	
	def merge(self, path):
		"""Return the given path relative to self.path."""
		if not path:
			return self.path
		p = ospath.expanduser(path)
		if ospath.isabs(p):
			return ospath.normpath(p)
		else:
			p = ospath.join(self.path, p)
			return ospath.abspath(ospath.normpath(p))
	
	def hash(self, algo, blocksize=None):
		"""
		Hash the file at self.path using the given algo; optional argument
		`blocksize` defaults to value returned by self.blocksizer().
		"""
		blocksize or self.blocksizer()
		try:
			h = hashlib.new(algo)
		except:
			import hashlib
			h = hashlib.new(algo)
		
		with open(self.path, 'rb') as f:
			b = f.read(blocksize)
			while len(b) > 0:
				h.update(b)
				b = f.read(blocksize)
		return h.hexdigest()
	
	def md5(self, blocksize=None):
		"""Hash using md5 algo."""
		return self.hash('md5', blocksize or self.blocksizer())
	
	def blocksizer(self, path=None):
		"""Recommended block size (4K-16M), based on size of file."""
		sz = ospath.getsize(path or self.path)
		for x in [12,14,20,23]:
			blocksize = 2**x
			if sz < blocksize:
				return blocksize
		return 2**24 # max
	
	def size(self, path=None):
		p = self.merge(path)
		return os.path.getsize(p)
	
	def stat(self, path=None):
		p = Path(self.merge(path))
		t = p.pathtype
		if t == 'l':
			return os.lstat(p.path)
		#elif t == 'f':
		else:
			return os.stat(p.path)
			
	
	# DIR
	def dir(self, path=None):
		"""
		Return a dir.Dir object for this path. Pass path string to merge.
		"""
		return trix.ncreate('fs.dir.Dir', self.merge(path))
	
	
	#
	#
	# WRAPPER
	#
	#
	def wrapper(self, **k):
		"""
		Returns a File-based object wrapping the fs object at this
		path. The default for files whose mime type can't be matched 
		here is fs.file.File.
		"""
		# MIME, VALIDATION
		mm = self.mime
		if self.isdir() or self.ismount():
			raise Exception('open-fail', xdata(
				path=self.path, reason='file-required', k=k
			))
		
		# Application
		if mm.type == 'application':
			
			# tar, tar.bz2, tar.gz, tgz
			if mm.subtype == 'x-tar':
				return trix.ncreate('fs.tar.Tar', self.path, **k)
			
			# zip
			elif mm.subtype == 'zip':
				return trix.ncreate('fs.zip.Zip', self.path, **k)
			
			# xlsx - for now, use zip, but there may be room for improvement
			elif mm.subtype == 'vnd.openxmlformats-officedocument.spreadsheetml.sheet':
				return trix.ncreate('fs.zip.Zip', self.path, **k)
			
			# json
			#elif mm.subtype == 'json':
			#	tj = trix.ncreate('data.transform.TransformJson')
			#	return trix.ncreate(
			#		'fs.tfile.TransformFile', tj, self.path, **k
			#	)
	
		# encoded
		elif mm.enc == 'bzip2':
			return trix.ncreate('fs.bzip.Bzip', self.path, **k)	
			
			#if mm.subtype == 'plain':
			#	return trix.ncreate('fs.bzip.Bzip', self.path, **k)
			#elif mm.subtype in ['csv', 'tab-separated-values']:
			#	return trix.ncreate('fs.csv.CSV', self.path, **k)
		
		# gzip
		elif mm.enc == 'gzip':
			return trix.ncreate('fs.gzip.Gzip', self.path, **k)
			#if mm.subtype == 'plain':
			#	return trix.ncreate('fs.gzip.Gzip', self.path, **k)
			#elif mm.subtype in ['csv', 'tab-separated-values']:
			#	return trix.ncreate('fs.csv.CSV', self.path, **k)
			
		# text csv	
		#elif mm.subtype in ['csv', 'tab-separated-values']:
		#	return trix.ncreate('fs.csv.CSV', self.path, **k)
		
		#
		# Default - for plain text or, as a default, any kind of file
		#
		return trix.ncreate('fs.file.File', self.path, **k)
	
	
	# READER
	def reader(self, **k):
		"""
		Return a reader for this object's path based on the mime type of
		the file there. If this Path object points to a tar or zip file,
		a member keyword must specify the member to read. In such cases,
		the returned Reader object will be suitable to the mime type of
		the specified member (as far as is supported by the fs package).
		
		Encoding-related kwargs are extracted and sent to the reader when
		it's created. All other (not encoding-related) kwargs are used to
		create any wrappers that may be needed to create this reader. 
		
		NOTE: Do not specify a 'mode'; this method must always rely on
		      the default mode for the type of wrapper that represents 
		      the file at this path.
		"""
		
		# Files with members will need to create a different kind of
		# object from what gets returned. Pop that key out of kwargs
		# before calling `wrapper`.
		member = k.pop('member', None)
		
		# now get the file wrapper object and return a reader
		wrapper = self.wrapper(**k)
		
		
		# -- container wrapper handling (tar/zip) --
		
		# If member is passed, it is required; the file type wrapper must
		# have a 'names' property.
		if member:
			try:
				wrapper.names
			except Exception as ex:
				raise type(ex)('fs-reader-fail', xdata(k=k, path=self.path,
						reason='fs-non-container', member=member, wrapper=wrapper
					))
			
			# make sure the specified member exists in the tar/zip file
			if not member in wrapper.names:
				raise KeyError('fs-reader-fail', xdata(k=k, path=self.path,
						reason='fs-non-member', member=member, wrapper=wrapper
					))
			
			# get correct file class by calling wrapper on member
			try:
				mpath = Path(member, affirm=None)
				
				# get a wrapper suitable to the member's filename
				mwrap = mpath.wrapper()
			except:
				# default is plain File
				mwrap = ncreate('fs.file.File')
			
			# get the original 'owner' stream for the memberwrapper to use
			ownerstream = wrapper.reader(member=member).detach()
			
			# create the member's wrapper
			try:
				rr = mwrap.reader(stream=ownerstream, **k)
			except BaseException as ex:
				raise type(ex)("err-reader-fail", ex.args, xdata(
						mpath=mpath, mwrap=mwrap, member=member,
						ownerstream=ownerstream
					))
			
			return rr
		
		# -- non-contaner handling --
		return wrapper.reader(**k)
	
	
	@classmethod
	def expand(cls, path=None, **k): # EXPAND
		"""
		Returns an absolute path.
		
		Keyword 'affirm' lets you assign (or restrict) actions to be
		taken if the given path does not exist. 
		 * checkpath - default; raise if parent path does not exist.
		 * checkfile - raise if `path` doesn't specify an existing file.
		 * checkdir - raise if full given path does not exist.
		 * makepath - create parent path as directory if none exists.
		 * makedirs - create full path as directory if none exists.
		 * touch - create a file at the given path if none exists.
		
		To ignore all validation, pass affirm=None.
		"""
		OP = os.path
		if path in [None, '.']:
			path = os.getcwd()
		
		if not OP.isabs(path): # absolute
			path = OP.expanduser(path)
			if OP.exists(OP.dirname(path)): # cwd
				path = OP.abspath(path)
			else:
				path = OP.abspath(OP.normpath(path))
		
		v = k.get('affirm', "checkpath")
		if (v=='checkfile') and (not OP.isfile(path)):
			raise ValueError('not-a-file', {'path' : path})
		elif (v=='checkpath') and (not OP.exists(OP.dirname(path))):
			raise ValueError('no-such-path', {'path' : OP.dirname(path)})
		if v:
			if OP.exists(path):
				if (v=='checkdir') and (not OP.isdir(path)):
					raise ValueError('not-a-directory', {'path' : path})
			else:
				if (v=='checkdir'):
					raise ValueError('no-such-directory', {'path' : path})
				elif v in ['makepath', 'touch']:
					if not OP.exists(OP.dirname(path)):
						os.makedirs(OP.dirname(path))
					if v == 'touch':
						Path(path).wrapper().touch()
				elif (v=='makedirs'):
					os.makedirs(path)
		
		return path




#
# FILE BASE
#
class FileBase(Path, EncodingHelper):
	"""Common methods fs.file.File and subclasses will need."""
	
	def __init__(self, path=None, **k):
		"""Pass file path with optional keyword arguments."""
		
		#
		# If `affirm` is "touch", prepare for its handling after Path is
		# initialized. By resetting the affirm value to 'makepath', the
		# way is clear for this object to call it's class-specific
		# `touch` method after Path is initialized here.
		#
		touch = (k.get('affirm') == 'touch')
		if touch:
			k['affirm'] = 'makepath'
		
		# init superclasses
		EncodingHelper.__init__(self, **k)
		Path.__init__(self, path, **k)
		
		# handle touch, if necessary
		if touch and not self.exists():
			self.touch()
	
	
	def __call__(self, item='.'):
		"""Returns path from containing directory."""
		p = Path(self.merge('..'))
		try:
			# this works if item is an integer index into this directory
			return p.__call__(self[item])
		except TypeError:
			# this works if item is a string path
			return p.__call__(item)
	
	# SET PATH - prevent changing path
	def setpath(self, path):
		"""Prevents changing of this file wrapper's path. """
		raise ValueError('fs-immutable-path', xdata())

	
	# TOUCH - touch file without possibility of "merging" the path.
	def touch(self, times=None):
		"""Touch this file."""
		with open(self.path, 'a'):
			os.utime(self.path, times)  
	
	
	# DIR
	def dir(self, path=None):
		"""
		Return a dir.Dir object for the directory containing this file. 
		Pass path string (default None) to merge from the directory
		containing this file.
		"""
		return trix.ncreate('fs.dir.Dir', self.merge('..')).dir(path)
	
	# COPY
	def copy(self, dest, **k):
		src = self.path
		dst = self.dir().merge(dest)
		try:
			shutil.copyfile(src, dst)
			if k.get('stat'):
				shutil.copystat(src, dst)
			if k.get('mode'):
				shutil.copymode(src, dst)
		except Exception as ex:
			raise type(ex)(ex.args, xdata(src=src, dst=dst, dest=dest, k=k))
	
	# MOVE
	def move(self, dest):
		src = self.path
		dst = self.dir().merge(dest)
		try:
			shutil.move(src, dst)
			Path.setpath(self, dst)
		except Exception as ex:
			raise type(ex)(ex.args, xdata(src=src, dst=dst, dest=dest))
	
	# RENAME
	def rename(self, dest):
		src = self.path
		dst = self.dir().merge(dest)
		try:
			os.rename(src, dst)
			Path.setpath(self, dst)
		except Exception as ex:
			raise type(ex)(ex.args, xdata(src=src, dst=dst, dest=dest))
	
	# REMOVE
	def remove(self):
		os.remove(self.path)





