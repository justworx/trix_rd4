#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *
from ...net.client import * #from ..client import *
from .irc_connect import *

BOT_CONFIG = "~/.config/trix/irc/bots/" # real config files
BOT_NCONFIG = "x/irc/config"            # conf templates            # <--- path changes


class Bot(Client):
	"""An irc bot object, containing one or more irc connections."""
	
	# the type for new connection objects
	DefType = IRCConnect
	
	
	def __init__(self, botname):
		"""
		Pass string `botname` - the bot's name. The bot will be started 
		if its config file exists in BOT_CONFIG.  Otherwise, a new 
		config for the given `botname` must be generated, so a series of 
		questions will appear in the terminal.
		
		NOTES: 
		 * The botname value is always reset to lower-case. 
		 * The BOT_CONFIG is: "~/.config/trix/irc/bots/";
		   The config file will be saved as <botname>.json, where 
		   <botname> is the `botname` string given to the constructor.
		"""
		
		#
		# BOT ID 
		# Users give a name to each of their bots.
		# Every bot config file in .cache config is named for its botname
		# in the format '~/.config/trix/irc/bots/<BOTID>.json'
		#
		self.__botname = str(botname).lower()
		
		
		#
		# CONFIGURATION
		#  - I want to make it so that changes to self.config can be
		#    storied by calling jconfig.save().
		#
		
		#
		# Use the `trix.util.jconfig` class to manage the config file.
		#	Load the config file at '~/.config/trix/irc/bots/<BOTID>.json'
		#
		self.__pconfig = BOT_CONFIG + "%s.json" % self.__botname
		
		#
		# LOAD CONFIG
		#  - This creates the self.__jconfig and self.__config members.
		#  - This also generates a new config file for `botname` if none
		#    currently exists.
		#
		try:
			self.__loadconfig()
		except KeyboardInterrupt:
			raise Exception("Bot configuration was canceled.")
		
		#
		# Finally, init the superclass
		#
		Client.__init__(self, self.config)
	
	
	
	def __del__(self):
		try:
			if self.active and self.running:
				self.shutdown()
			else:
				if self.running:
					self.stop()
				if self.active:
					self.close()
		except:
			pass # maybe try trix.log here
	
	
	@property
	def botname (self):
		"""Return the bot name, as given to the Bot constructor."""
		return self.__botname
	
	@property
	def pconfig(self):
		"""Return the config path."""
		return self.__pconfig
	
	@property
	def jconfig(self):
		"""
		Return the JConfig object for this config file. This object can
		be used to edit config files. Once edited, the files may be seved
		by calling `JConfig.save()`.
		"""
		return self.__jconfig
	
	@property
	def config(self):
		"""Return the bot configuration dict, as loaded on init."""
		return self.__config
	
	
	
	
	#
	# --------- override methods -----------------
	#
	
	#	OPEN
	def open(self):
		try:
			# for except clause, in case it doesn't get far enough to 
			# define one of these...
			connid = None
			config = None
			
			# get the connections dict from self.config
			cconnections = self.config.get('connections', {})
			
			# loop through each connections key
			for connid in cconnections:
				
				# get this connection's config
				config = cconnections[connid]
				
				# if the connection is marked inactive, skip it
				if not config.get("active", True):
					continue
				
				#
				# At this point, DefType is irc_connect, and variables are:
				#  * connid = the connection-dict's key (network-botid)
				#  * config = the connection's value
				#
				self.connect(connid, config)
				
				Client.open(self)
		
		except Exception as ex:
			Client.close(self)
			raise type(ex)("err-bot-fail", xdata(
					detail="bot-open-fail", connid=connid
				))
	
	
	#	RUN
	def run(self):
		"""
		Start running all connections for this Bot.
		"""
		try:
			Client.run(self)
		except Exception as ex:
			self.shutdown()
			raise
	
	
	# HANDLE-DATA
	def handleio(self, conn):
		"""
		This method is called when `trix.net.client.Client` receives
		input from the IRC server.
		"""
		conn.io()
	
	
	# HANDLE-X (Exception)
	def handlex(self, connid, xtype, xargs, xdata):
		if connid in self.conlist:
			conn = self[connid]
			if xtype == SockFatal:
				pass
			elif xtype == KeyboardInterrupt:
				self.pause()
				Console().console()
	
	
	# ADD CONFIG
	def addconfig(self):
		"""
		Add an additional connection configuration for this bot.
		Note that this will cause input from multiple servers to be
		displayed in the same terminal session if self.show is True.
		"""
		self.__addconfig(self.botname)
	
	
	#
	# --------- private methods -----------------
	#
	
	#
	# LOAD CONFIG
	#  - This creates the self.__jconfig and self.__config members.
	#  - This also generates a new config file for `botname` if none
	#    currently exists.
	#
	def __loadconfig(self):
		"""
		Load a this bot's config file from ~/.config/trix/irc/bots (or
		wherever BOT_NCONFIG says).
		
		If no config file exists at for this bot, a Form object will
		present a list of questions that allow the bot config to be
		generated with one connection.
		"""
		botname = self.__botname
		self.__jconfig = trix.jconfig(self.__pconfig)
		self.__config = self.__jconfig.obj
		if not self.__config.get('connections'):
			self.__addconfig(botname)
	
	#
	#
	# ADD CONFIG
	#  - Create a new configuration file for a given `botname`
	#
	def __addconfig(self, botname):
		
		#
		self.__config.setdefault('botname', botname)
		self.__config.setdefault('connections', {})
		
		
		# load the form module and fill out the form
		fmod = trix.nmodule("app.form")
		fcnf = BOT_NCONFIG+"/irc_config.conf"
		form = fmod.Form(fcnf)
		
		# use Form to get a connection configuration
		condict = form.fill()
		if not condict:
			raise KeyboardInterrupt()
			
		# save network name and configid for use below
		network = condict.get('network')
		configid = "%s-%s" % (network, botname)
		
		#
		# LOAD FRESH PLUGIN CONFIG
		#  - Add plugin config for each connection; plugin config must
		#    be duplicated so that each connection retains fine-tuneable 
		#    control over its own set of plugin objects.
		#
		plugin_config = trix.nconfig("%s/irc_plugin.conf" % BOT_NCONFIG)
		
		# add the connection for `botname`
		self.config['connections'][configid] = condict
		self.config['connections'][configid]['plugins'] = plugin_config
		
		# save the configuration
		self.jconfig.save()
		
		return self.jconfig.obj


