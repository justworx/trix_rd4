#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ..x.output import * #trix,sys
from ..util.xinput import *
from ..app.event import *

#
# ---- CONSOLE -----
#

class Console(BaseOutput):
	"""
	Base class for an interactive command-line user interface.
	
	UNDER CONSTRUCTION
	 - This is a very early rewrite of the original (rd3) Console 
	   class. Some (not much) of that original Console will be used 
	   here, but the general scheme may turn out to be completely 
	   different.
	
	NOTE:
	 - Console accepts an 'output' kwarg for writing, but it must NOT
	   be based on the Output class. There is no pausing the console!
	
	"""
	
	# This will be changed to False after initial development.
	Debug = True 
	
	def __init__(self, config=None, **k):
		
		config = config or {}
		config.update(k)
		
		BaseOutput.__init__(self, config)
		
		# debugging
		self.__debug = config.get('debug', self.Debug)
		
		# plugins
		self.__plugins = {}
		self.__plugins['calc'] = trix.ncreate(
				"app.plugin.calc.Calc", "calc", self, {}
			)
		self.__plugins['dir'] = trix.ncreate(
				"app.plugin.dir.Dir", "dir", self, {}
			)
	
	
	
	@property
	def debug(self):
		"""Console prompt."""
		return self.__debug
	
	
	@property
	def jformat(self):
		"""Object display format (default: JDisplay)."""
		try:
			return self.__jformat
		except:
			self.__jformat = trix.formatter(f='JDisplay')
			return self.__jformat
	
	
	@property
	def prompt(self):
		"""Console prompt."""
		return "> "
	
	
	@property
	def plugins(self):
		"""Return plugins dict."""
		return self.__plugins

	
	
	# BANNER
	def banner(self):
		"""Display entry banner."""
		self.writeline("\n#\n# CONSOLE\n#\n")
	
	
	
	#
	# CREATE EVENT
	#
	def create_event(self, commandLineText):
		"""Returns a TextEvent."""
		return LineEvent(commandLineText)
	
	
	
	#
	# CONSOLE - Run the console.
	#
	def console(self):
		"""Call this method to start a console session."""
		self.banner()
		self.__active = True
		while self.__active:
			evt=None
			try:
				# get input, create Event
				line = xinput(self.prompt).strip()
				
				# make sure there's some text to parse
				if line:
					# get and handle event
					evt = self.create_event(line)
					self.handle_input(evt)
			
			except (EOFError, KeyboardInterrupt) as ex:
				# Ctrl-C exits this prompt with EOFError; end the session.
				self.__active = False
				self.writeline("\n#\n# Console Exit\n#\n")
				raise KeyboardInterrupt("end-console-session")
			
			except BaseException as ex:
				#
				# Handle other exceptions by displaying them
				#
				self.writeline('') # get off the "input" line
				self.writeline("#\n# ERROR: %s\n#" % str(ex))
				self.writeline(self.jformat(xdata()))
		
			
	
	
	# HANDLE INPUT
	def handle_input(self, e):
		"""Handle input event `e`."""
		
		if e.argc and e.argv[0]:
			
			#
			# check plugins first
			#
			for p in self.__plugins:
				self.__plugins[p].handle(e)
				if e.reply:
					self.writeline (str(e.reply))
					return
			
			#
			# handle valid commands...
			#
			
			if e.argvl[0] == 'plugins':
				# list plugin names
				self.writeline(" ".join(self.plugins.keys()))
			
			elif e.argvl[0] == 'exit':
				# leave the console session
				self.__active = False
			
			#
			# CHECK FIRST ARG!
			#  - There's always at least one argument, even if it's ''.
			#    In this case, nothing (or only white space) was entered,
			#    so just hit the next line. Otherwise, it's an unknown 
			#    command, so complain.
			#
			elif e.argvl[0]:
				raise Exception(xdata(error="unknown-command", args=e.argv))




