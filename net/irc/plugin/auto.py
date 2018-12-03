#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

# --- UNDER CONSTRUCTION ---

from . import *

class IRCAuto(IRCPlugin):
	"""Auto -voice, -kick, -tell, etc..."""
	
	connected = False
	configpath = '~/.cache/trix/auto/%s'
	
	def __init__(self, pname, bot, config=None, **k):
		IRCPlugin.__init__(self, pname, bot, config, **k)
		
		# get the main config file
		p = self.configpath % 'automode.json'
		r = trix.path(p, affirm='touch').reader(**self.ek)
		self.__automode = trix.jparse(r.read() or "{}")
	
	
	def addfile(self, autoid, filename):
		"""
		Add key `autoid` with value `filename` to the `auto` config
		file (at `self.configpath`) and create a blank file there.
		"""
		p = self.configpath % filename
		w = trix.path(p, affirm='touch').wrapper(**self.ek).writer()
		w.write("{}")
	
	
	#def openfile(
	
	#
	# now i'm thinking this cache file stuff may need to be a little
	# more generic. gonna sleep on it. 
	#
	
