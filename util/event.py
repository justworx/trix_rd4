#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *
from ..data.scan import *

import time, ast


#
#
# BASIC EVENT
#  - Functions/Properties common to all Event objects.
#
#
class Event(object):
	"""Base Event object."""
	
	def __init__(self, *a, **k):
		"""Store args/kwargs; Manage basic reply."""
		
		self.__a = a
		self.__k = k
		
		self.__trequest = time.time()
		self.__treply = None
		self.__reply = None
		self.__error = None
	
	
	@property
	def reply(self):
		"""The reply sepecified by whatever is handling this event."""
		return self.__reply
	
	@reply.setter
	def reply(self, data):
		self.__reply = data
		self.__treply = time.time()
	
	
	@property
	def error(self):
		"""Error during processing; eg, xdata()"""
		return self.__error
	
	@error.setter
	def error(self, error):
		self.__error = error
	
	
	@property
	def requesttime(self):
		"""Request time (set on __init__) - time.time()"""
		return self.__trequest
	
	@property
	def replytime(self):
		"""Reply time - time.time()"""
		return self.__treply
	
	@property
	def processtime(self):
		"""Time in microseconds between object creation and reply."""
		if self.replytime and self.requesttime:
			return self.replytime - self.requesttime
		return None
	
	
	@property
	def argv(self):
		"""
		List of arguments received by the constructor. This is typically
		overridden by subclasses that parse text lines to determine the
		valid arguments.
		"""
		return self.__a
	
	@property
	def argc(self):
		"""
		Argument count - The number args received by the constructor.
		For subclasses that manipulate arguments (eg, by parsing text
		into a list of arguments), this may be a different from the 
		number of actual arguments given to the constructor. For objects
		of this class, however, it will always be the same as the number
		of arguments received in *a.
		"""
		try:
			return self.__argc
		except:
			self.__argc = len(self.argv)
			return self.__argc
	
	@property
	def argvc(self):
		"""Arg-v strings converted to all-caps."""
		try:
			return self.__argvc
		except:
			self.__argvc = []
			for a in self.argv:
				try:
					self.__argvc.append(a.upper())
				except AttributeError:
					self.__argvc.append(a)
			
			return self.__argvc
	
	@property
	def argvl(self):
		"""
		Arg-v strings converted to lowercase. Non-string objects are
		left unchanged.
		"""
		try:
			return self.__argvl
		except:
			self.__argvl = []
			for a in self.argv:
				try:
					self.__argvl.append(a.lower())
				except AttributeError:
					self.__argvl.append(a)
			return self.__argvl
	
	@property
	def kwargs(self):
		"""Returns any keyword arguments received by the constructor."""
		return self.__k

	@property
	def dict(self):
		"""Debugging utility - returns dict."""
		return self.getdict()
	
	
	
	def arg(self, i, default=None):
		"""Return existing arg at offset `i`, or `default`."""
		try:
			return self.argv[i]
		except:
			return default
	
	
	def getdict(self):
		return {
			'argc'  : self.argc,
			'argv'  : self.argv,
			'reply' : self.reply,
			'error' : self.error
		}
	
	
	# debugging
	def display(self, x=None, **k):
		"""This event's `self.dict`, printed in json display format."""
		trix.display(x or self.dict, **k)



#
#
# TEXT EVENT
#
#
class TextEvent(Event):
	"""
	Package a single line of text into an event structure.
	
	Properties:
		line : full line as received
		text : alias for line
		argv : list of arguments [text.split()]
		argc : count(argv)
		argvl: same as argv, but all lower-case
		argvc: same as argc, but all capital letters
		dict : all of the above, in a dict.
	
	The line of text is split on spaces. The self.argv property returns
	a list of all the words. The first word is typically considered to
	be a command while following words are its arguments. 
	
	NOTE:
	Subclasses may separate args from other data, as is the case of 
	`trix.net.irc.irc_event.IRCEvent`. However, even in that case the
	conceptual command - intended for a bot - is the first item
	in IRCEvent.argv and subsequent items in `argv` are the command's
	parameters. Other items of - something like "meta-data" - are
	stored in additional "irc-only" properties (eg, the irccmd which
	is the server's "PRIVMSG" or "NOTICE" command), but the received
	text works just like here in TextEvent: The conceptual command 
	is the first item in argv and the rest are that command's 
	parameters.
	
	NOTE ALSO:
	While self.line and self.text are always the same for TextEvent,
	they may be different in subclasses. In IRCEvent, the `line`
	value may include irc formatting codes (eg., bold, italic, or
	colors, etc..), but text will always be deformatted. Therefore,
	self.text should be called in cases where machine-processing 
	does not require the use of formatting, while self.line should
	be used if that format info is needed.
	"""
	
	def __init__(self, cline):
		"""
		Pass one line of text that is to be processed as a command. 
		"""
		Event.__init__(self, cline)
		self.__line = cline
	
	@property
	def line(self):
		"""The full line of text, as given to the constructor."""
		return self.__line
	
	@property
	def text(self):
		"""
		The full line of text, as given to the constructor. 
		
		Subclasses may alter this in cases where formatting or other 
		data - data not thought of as "part of the text" - need to be
		removed.
		"""
		return self.__line
	
	@property
	def argv(self):
		"""
		Each individual word stored as a list item.
		"""
		try:
			return self.__argv
		except:
			self.__argv = self.text.split(' ')
			return self.__argv
	
	@property
	def dict(self):
		"""Debugging utility - returns dict."""
		return {
			'line'  : self.line,
			'text'  : self.text,
			'argc'  : self.argc,
			'argv'  : self.argv,
			'argvc' : self.argvc,
			'argvl' : self.argvl,
			'reply' : self.reply
		}



#
#
# LINE EVENT (as in Command-line.)
#
#
class LineEvent(Event):
	"""A Command-based event; Splits arguments using Scanner."""
	
	ARGPARSE = [
		lambda x: int(float(x)) if float(x)==int(float(x)) else float(x),
		lambda x: trix.jparse(x),
		lambda x: ast.literal_eval(x),
		lambda x: str(x)
	]
	
	@classmethod
	def argparse(cls, x):
		"""
		Type cast string `x` to int, float, dict, or list, if possible,
		or return the original string.
		"""
		errors = []
		for L in cls.ARGPARSE:
			try:
				return L(x)
			except Exception as ex:
				errors.append(xdata())
		
		# if all attempts to parse argument fail, raise an exception
		raise Exception("parse-fail", errors=errors)
	
	
	def __init__(self, commandline, **k):
		"""
		Pass full command line text, plus optional kwargs. The command
		line is scanned for string, int, float, list, and dict structures
		and an array of type-cast values is returned.
		
		Otherwise, it's just like Event, with first argument being the
		command, followed by individual arguments.
		
		>>> e = LineEvent('do [1, "two", {3:{4: "the number four"}}]')
		>>> e.arg(0)          # 'do'
		>>> e.arg(1)[2][3][4] # 'the number four'
		"""
		
		s = Scanner(commandline)
		a = s.split()
		r = []
		try:
			for x in a:
				r.append(self.argparse(x))
			
			Event.__init__(self, *r, **k)
		
		except Exception as ex:
			raise type(ex)(xdata(line=commandline, args=a, r=r))
	
	@property
	def text(self):
		"""
		A list of arguments as given to the constructor, but with each
		item having been coerced to strings. 
		"""
		try:
			return self.__text
		except:
			args = []
			for a in self.argv:
				args.append(str(a))
			self.__text = " ".join(args)
			return self.__text



#
#
# COMMAND EVENT
#
#
class Command(Event):
	"""An Event that separates the command from the args."""
	
	def __init__(self, command, *a, **k):
		Event.__init__(self, *a, **k)
		self.__command = command
	
	@property
	def cmd(self):
		return self.__command
	
	@property
	def command(self):
		return self.__command
	
	def getdict(self):
		d = Event.getdict(self)
		d['command'] = self.command
		return d


