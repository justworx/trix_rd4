#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from trix.app.plugin import *


class Dir(Plugin):
	"""Directory exploration via console."""
	
	COMMANDS = {
		'cd'   : lambda d,*a: d.cd(*a),
		'ls'   : lambda d,*a: d.ls(*a),
		'mv'   : lambda d,*a: d.mv(*a)
	}
	
	def __init__(self, pname, owner, config=None, **k):
		config = config or {}
		config.update(k)
		Plugin.__init__(self, pname, owner, config, **k)
		
		p = config.get('path', '.')
		self.__dir = trix.path(p).dir()
	
	
	@property
	def dir(self):
		"""Return the dir object."""
		return self.__dir
	
	
	#
	# HANDLE
	#	
	def handle(self, e):
	
		cmd = e.argvl[0]
		if cmd == 'path':
			self.reply(e, self.__dir.path)
		
		elif cmd == 'cd':
			try:
				self.__dir.cd(e.argv[1])
				self.reply(e, self.__dir.path)
			except Exception as ex:
				raise type(ex)(xdata(dir=self.__dir, e=e))
		
		elif cmd in self.COMMANDS:
			x = self.COMMANDS[cmd]
			#print (x)
			a = e.argv[1:]
			r = x(self.__dir, *a)
			if r:
				self.reply(e, ", ".join(r))

