#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

import weakref
from .bfile import * # trix, stream, enchelp
from ..util.stream.buffer import *

class Archive(FileBase):
	"""Archive files that contain member files (Zip and Tar)."""
	
	def __init__(self, path, **k):
		"""Pass archive file path and kwargs relevant to file type."""
		
		#
		# Keep changed members in __writers dict. Each key is an archive 
		# member's name, and its value is a Buffer object with the text
		# to be stored when this archive is flushed - rewritten into a
		# new archive with removals excluded, changed and unchanged (but
		# not removed) members.
		#
		self.__writers = {}
		self.__readers = {}
		self.__deleted = []
		self.__openk = k
		
		FileBase.__init__(self, path, **k)
	
	
	# DEL
	def __del__(self):
		try:
			if self.__writers or self.__deleted:
				self.flush()
		except:
			pass
	
	@property
	def openk(self):
		return dict(self.__openk)
	
	@property
	def deleted(self):
		return self.__deleted
	
	@property
	def writers(self):
		return self.__writers.keys()
	
	
	
	#
	# ABSTRACT PROPERTIES AND METHODS
	#  - All classes based on Archive must implement these.
	#
	@property
	def members(self):
		"""The member objects within the archive."""
		raise NotImplementedError("abstract-property-required", 'members')
	
	@property
	def names(self):
		"""List of the names of member objects in this archive."""
		raise NotImplementedError("abstract-property-required", 'names')
	
	# ARCH-READ
	def archread(self, member, **k):
		"""Read a single member from the archive."""
		raise NotImplementedError("abstract-method-required", 'archread')
	
	# ARCH-STORE
	def archstore(self, membergen, **k):
		"""Write all non-deleted members to the new archive."""
		raise NotImplementedError("abstract-method-required", 'archstore')
	
	
	
	#
	# ------------ ARCHIVE METHODS ------------
	#
	
	#
	# READ
	#
	def read(self, member, **k):
		"""
		Return the entire contents of the member. Use "mode", "encoding",
		and "errors" kwargs to tailor the result type.
		"""
		return self.reader(member, **k).read()
	
	# READER
	def reader(self, member, **k):
		"""
		Return a Buffer.reader() to read the given member. Pass Reader
		kwargs to specify how data should be read. Buffer kwargs are also
		accepted, but are only applicable on the first call for any given
		member.
		"""
		if member in self.__writers:
			b = self.__writers[member]
		elif member in self.__readers:
			b = self.__readers[member]
		else:
			bk = trix.kpop(k, 'max_size mode encoding')
			b = Buffer(**bk)
			b.write(self.archread(member, **k))
			self.__readers[member] = b
		
		b.seek(0)
		return weakref.proxy(b.reader(**k))
	
	
	
	#
	# WRITE
	#
	def write(self, member, data, **k):
		"""Write the new contents of the member."""
		self.writer(member, **k).write(data)
	
		
	# WRITER
	def writer(self, member, **k):
		"""
		Return a Buffer.writer() to write to the given member. Pass Writer
		kwargs to specify how data should be read. Buffer kwargs are also
		accepted, but are only applicable on the first call (when the 
		buffer is first created).
		"""
		
		# a buffer already writable
		if member in self.__writers:
			b = self.__writers[member]
		
		# a buffer that was a reader, now becomes a writer
		elif member in self.__readers:
			b = self.__readers[member]
			del(self.__readers[member])
		
		else:
			mxsz = k.pop('max_size', None)
			b = Buffer(mxsz, **k)
			try:
				# an existing member not yet read or written to
				b.write(self.archread(member, **k))
			except KeyError:
				# A new buffer not in the archive (which will be written (to
				# a new archive file) when flush() is called.
				pass
		
		# store the member's buffer
		self.__writers[member] = b
		
		# if this member name has been deleted, undelete it (or it won't
		# get written when it's supposed to!)
		if member in self.__deleted:
			self.__deleted.remove(member)
		
		# start at the beginning; return a proxy to the buffer's writer
		b.seek(0)
		return weakref.proxy(b.writer(**k))
	
	
	
	#
	# DELETE
	#
	def delete(self, member):
		"""Mark the given member for deletion on the next flush."""
		self.__deleted.append(member)
		if member in self.__readers:
			del(self.__readers[member])
		if member in self.__writers:
			del(self.__writers[member])
	
	
	
	#
	# UNDO CHANGES
	#
	def undelete(self, member):
		"""Remove a member from the deletion list."""
		if member in self.__deleted:
			self.__deleted.remove(member)
	
	def unwrite(self, member):
		"""Remove all changes to member since the last flush."""
		if member in self.__writers:
			del(self.__writers[member])
	
	def revert(self, member=None):
		"""
		If member is specified, undelete/undo any writes. Otherwise, undo
		all writes/deletes since the last flush.
		"""
		if member:
			self.undelete(member)
			self.unwrite(member)
		else:
			self.__writers={}
			self.__deleted=[]
	
	
	
	#
	# MEM-GEN
	#
	def memgen(self):
		"""Used internally by subclasses to write archive members."""
		# 
		# BUILD NAME LIST
		#  - Build a list of names to be checked and, if appropriate,
		#    written to the ARCHNEW file.
		#
		names = []                           # start with blank list
		names.extend(self.names)             # add all archive names
		names.extend(self.__writers.keys())  # add all writer names
		names = set(names)                   # make the list unique
		
		for name in names:
			# Copy existing files and write new self.__writers buffers
			# to the new (`archnew`) archive.
			if not (name in self.__deleted):
				if name in self.__writers:
					b = self.__writers[name]
				elif name in self.__readers:
					b = self.__readers[name]
				else:
					# copy unedited members
					b = Buffer()
					b.write(self.archread(name))
				
				# seek start and yield a dict
				b.seek(0)
				d = dict(member=name, buffer=b)
				yield (d)
	
	
	#
	# FLUSH
	#
	def flush(self):
		"""
		Flush is called automatically when an ARchive object is destroyed.
		If any changes are buffered, the archive will be rewritten to
		reflect the current members and their content.
		""" 
		
		#
		# Don't do anything unless there are write buffers present.
		# If there are no writers, there are no changes.
		#
		if self.__writers or self.__deleted:
			
			# store self.path
			TRUEPATH = self.path
			TYPE = type(self) # either Zip or Tar
			try:
				#
				# ARCHNEW
				#  - create the new archive object using a temporary name,
				#    "#PATH#/#FILENAME#.new". EG, 'myArchive.tar.gz.new'.
				#
				ARCHNEW = "%s.new" % TRUEPATH
				krgs = self.openk
				krgs['affirm'] = 'touch'
				archnew = TYPE(ARCHNEW, **krgs)
				
				# write all undeleted members to the ARCHNEW file
				archnew.archstore(iter(self.memgen()))
				
				#
				# HANDLE THE BACKUP FILE
				#  - If there's an older backup file, remove it so we can 
				#    replace it with the current file.
				#
				BACKUP = ".bu.%s" % self.name
				x = FileBase(BACKUP)
				if x.exists():
					x.remove()
				
				#
				# RENAME THIS FILE
				#  - Rename the current file to ".#FILENAME#.bu"
				#  - Remember: `rename` resets self.path automatically, so 
				#    this file's internal self.path is now ".#FILENAME#.bu",
				#    which has just been removed.
				#
				self.rename(BACKUP)
				
				#
				# RENAME THE NEW FILE
				#  - Rename the newly-written archive to the name this object
				#    previously held. Again, `rename` resets self.path 
				#    automatically.
				#  - However, that's the new file object, not THIS object, so
				#    there's one more step to make the new file the property
				#    of this object...
				#
				archnew.rename(TRUEPATH)
				
				#
				# CHANGE INTERNAL FILE PATH
				#  - Make the new version of the archive the property of this
				#    object.
				#  - The old archive object `archnew` is done when this method
				#    exits. This object will now have its path.
				#
				Path.setpath(self, TRUEPATH)
				
				# clear all the buffers
				self.__writers={}
				self.__readers={}
				self.__deleted=[]
			
			except Exception as ex:
				#
				# I'm not too sure what needs to be done in the case of an
				# exception. I guess... 
				#  1. rename this file to whatever.restore
				#  2. rename the archnew file to this archive's real name
				#  3. reset self.path to the original file's path
				#
				# I guess I need to think some more on this. So far, there's
				# been no exception to help me see what might go wrong. I'm
				# not sure whether to hope for some errors! The whole thing's
				# pretty simple - maybe this catch isn't really needed. I do
				# need to think some more about this. TODO: Think some more!
				#
				raise
