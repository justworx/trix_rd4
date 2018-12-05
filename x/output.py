#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ..util.enchelp import * # trix, sys
from ..util.signals import *
from ..util.stream.buffer import *

#
# BASE OUTPUT - Non-pause-able output handler.
#
class BaseOutput(EncodingHelper):
	"""
	Provides the basic output mechanism required by Output and by the
	app/Console class.
	
	BaseOutput has no awareness of the pause status - it always write
	when write is called, regardless of the value of Output.pause().
	This class is used only by Console, which must display text during
	any pause state.
	"""
	
	def __init__(self, config=None, **k):
		"""
		Pass optional config dict. Optional kwargs update config values. 
		
		Config keys include:
		 * output: Any output stream object with a write method. Default
		           is sys.stdout.
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
		
		EncodingHelper.__init__(self, config)
		
		# config for Output
		self.__newl = config.get('newl', DEF_NEWL)
		
		# store config for reference
		self.__config = config
		
		# create buffer for paused buffering
		self.__output = config.get("output", sys.stdout)
		self.__writer = self.__output
	
	
	@property
	def config(self):
		"""BaseOutput and subclasses share this config dict."""
		return self.__config
	
	@property
	def writer(self):
		"""For BaseOutput, writer is the self.output."""
		return self.__writer
	
	@property
	def output(self):
		"""Instantly writes output regardless of pause status."""
		return self.__output
	
	@property
	def newl(self):
		"""Newline character(s). Given in config."""
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
		
		# BaseOutput always writes text immediately; there is no 
		# awareness here of the pause status.
		self.output.write(text)

	


#
#
# OUTPUT - Pauseable output.
#
#
class Output(BaseOutput):
	"""Management of "pausable" text output."""
	
	# default pause-buffer size: 16K
	PauseBufferSz = 2**14
	
	def __init__(self, config=None, **k):
		"""
		Pass optional config dict with parameters for EncodingHelper and
		Output. Optional kwargs update config values. 
		
		Config keys specific to this class:
		 * bufsz : Initial pause-buffer size (default, 16K). This is NOT
		           a maximum size, but rather the size at which the temp
		           buffer storage will resort to writing to disk.
		"""
		
		BaseOutput.__init__(self, config, **k)
		
		# defaults for Buffer
		config.setdefault("bufsz", self.PauseBufferSz)
		
		# create buffer for paused buffering
		self.__buffer = Buffer(**self.__config)
		self.__writer = self.buffer.writer()
	
	
	
	def __del__(self):
		self.__buffer = None
	
	
	@property
	def buffer(self):
		"""Buffered content, displayed only when pause-state is False."""
		return self.__buffer
	
	@property
	def writer(self):
		"""For Output, writer is the buffer's writer."""
		return self.__writer
	
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
	

