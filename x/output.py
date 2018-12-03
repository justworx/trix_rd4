#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.enchelp import * # trix, sys
from ..util.stream.buffer import *


class Output(EncodingHelper):
	"""Output management."""
	
	# default pause-buffer size: 16K
	PauseBuffer = 2**14
	
	def __init__(self, config=None, **k):
		"""
		Pass optional config dict. Optional kwargs update config values. 
		
		Config keys include:
		 * output: Any output stream object with a write method. Default
		           is sys.stdout.
		 * bufsz : Initial pause-buffer size (default, 16K). This is NOT
		           a maximum size, but rather the size at which the temp
		           buffer storage will resort to writing to disk.
		 * newl  : Value for newline separation, in ["\r","\n","\r\n"].
		           Default is `trix.DEF_NEWL`.
		
		Encoding-related values should be provided via config or kwargs.
		Default encoding is trix.DEF_ENCODE.
		"""
		
		config = config or {}
		config.update(k)
			
		# defaults for EncodingHelper
		config.setdefault("encoding", DEF_ENCODE)
		config.setdefault("errors", "replace")
		
		# defaults for Buffer
		config.setdefault("bufsz", self.PauseBuffer)
		
		# config for Output
		self.__newl = config.get('newl', DEF_NEWL)
		
		# store config for reference
		self.__config = config
		
		# create buffer for paused buffering
		self.__buffer = Buffer(**self.__config)
		self.__writer = self.buffer.writer()
		self.__output = sys.stdout
	
	
	
	def __del__(self):
		self.__buffer = None
	
	
	@property
	def config(self):
		return self.__config
	
	@property
	def buffer(self):
		return self.__buffer
	
	@property
	def writer(self):
		return self.__writer
	
	@property
	def output(self):
		return self.__output
	
	@property
	def newl(self):
		return self.__newl
	
	
	
	#
	# WRITE-LINE
	#
	def writeline(self, text):
		"""Write (or Buffer) text with newline appended."""
		self.write(text + self.newl)
	
	#
	# WRITE
	#
	def write(self, text):
		"""Write (or Buffer) text, depending on pause status."""
		
		# add text to buffer
		self.writer.write(text)
		
		# Unless paused, print anything that's buffered, then 
		# print and reset the buffer.
		if not self.paused():
			self.flushbuffer()
	
	#
	# FLUSH BUFFER
	#
	def flushbuffer(self):
		"""
		Write buffered content to output.
		
		This method is called by `self.write` before any text is written
		to the output buffer.
		
		The `Output` class is not intended to be threaded, but does serve
		as base for Runner and potentially other threadable classes that 
		may need the ability to flush buffered text immediately after a 
		change is detected in the pause status.
		"""
		if self.buffer.tell():
			self.output.write(self.buffer.read())
			self.output.flush()
			self.buffer.seek(0)
			self.buffer.truncate()
	
	
	
	
	#
	#
	# ---- pause/resume = class-level methods/values-----
	#
	#

	__interrupted = False
	
	@classmethod
	def paused(cls):
		"""Return True if paused, else False."""
		return cls.__interrupted
	
	@classmethod
	def pause(cls):
		"""Pause output. (Buffer until resume.)"""
		cls.__interrupted = True
		
	@classmethod
	def resume(cls):
		"""Resume. Display buffered output.""" 
		cls.__interrupted = False
	
	@classmethod
	def pausetoggle(cls, *a):
		"""Toggle pause status to it's opposite boolean value."""
		cls.__interrupted = not cls.__interrupted
	



# ----------------------------------------------------------------
#
# SIGNAL HANDLING - EXPERIMENTAL!
#
# This feature is new and experimental. There may be changes in
# future versions. This section may be moved, or removed entirely.
# 
# The purpose of this is to add signal handling to the Output class, 
# (which is the base class for Runner) so that pause/resume features
# may be added to Runner objects.
# 
# About the line of code below:
#  - trix.signals() returns a util.signals.Signals class with `add`
#    and `rmv` methods.
#  - The add method here is adding handling for signal 2, SIGINT,
#    which is associated with KeyboardInterrupt exceptions.
#  - Output.pausetoggle is a classmethod that sets the pause status
#    for all classes based on trix.util.Output.
#  - The transparent keyword is True, so the KeyboardInterrupt error
#    associated with this signal will not be captured/constrained,
#    but will fall through to the enclosing situation (eg, the python
#    interpreter, a script, whatever...) and be handled as though
#    the signal hadn't been intercepted.
#
# See trix.util.signals doc/help for more information.
#
# ----------------------------------------------------------------
trix.signals().add(2, Output.pausetoggle, transparent=True)




