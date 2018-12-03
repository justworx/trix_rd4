#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *
from ..connect import *
from .irc_connect import *
from .irc_event import *


class IRCConnect(Connect):
	"""An IRC Connection."""
	
	debug = True
	
	def __init__(self, config=None, **k):
		"""Pass a config dict."""
		
		config = config or {}
		config.update(k)
		config.setdefault('encoding', DEF_ENCODE)
		config.setdefault('errors', "replace")
		
		self.__config = config
		self.__pconfig = config.get('plugins', {})
		
		# required config
		self.__network = config['network']
		self.__owner   = config['owner']
		self.__host    = config['host']
		self.__port    = config['port']
		self.__nick    = config['nick']
		
		# config that defaults to nick
		self.__user     = config.get('user', self.__nick.lower())
		self.__realname = config.get('ident', self.__nick.lower())
		
		# connection objects/info
		self.__paused    = False
		self.__plugins   = {}
		self.__ginfo     = {}
		self.__chantypes = '#'
		self.__lineq     = trix.ncreate('util.lineq.LineQueue')
		self.__show      = config.get('show', self.debug) # print lines

		# runtime values
		self.pi_update = time.time()
		self.pi_interval = config.get('pi_interval', PLUG_UPDT)
		
		# plugin management - runtime add/remove
		self.pm_add = []
		self.pm_rmv = []
		
		# load plugins, if any
		for pname in self.__pconfig:
			if self.__pconfig[pname].get('active', True):
				self.__ginfo[pname] = {}
				pi = self.__plugin_load(pname)
				if pi:
					self.__plugins[pname] = pi
		
		#
		# initialize superclass
		#  - Connect opens a connection to the server immediately.
		#  - At this point, we must be ready to handle input.
		#
		Connect.__init__(self, (self.__host, self.__port),
				encoding = config.get('encoding', 'utf_8'),
				errors   = config.get('errors', 'replace')
			)
		
		# register the connection
		self.register()
	
	
	
	
	# ----------------------------------------------------------------
	# PROPERTIES
	# ----------------------------------------------------------------
	@property
	def config(self):
		return self.__config
	
	@property
	def network(self):
		return self.__network
	
	@property
	def host(self):
		return self.__host
	
	@property
	def port(self):
		return self.__port
	
	@property
	def nick(self):
		return self.__nick
	
	@property
	def user(self):
		return self.__user
	
	@property
	def realname(self):
		return self.__realname
	
	@property
	def paused(self):
		return self.__paused
	
	@property
	def pconfig(self):
		return self.__pconfig
	
	@property
	def plugins(self):
		return self.__plugins
	
	@property
	def ginfo(self):
		return self.__ginfo
	
	@property
	def chantypes(self):
		return self.__chantypes
	
	@property
	def owner(self):
		return self.__owner
	
	@property
	def show(self):
		return self.__show
	
	@show.setter
	def show(self, b):
		self.__show = bool(b)
	
	
	#
	# register connection
	#
	def register(self):
		"""Register connection with the irc server."""
		
		nick = self.nick
		user = self.user
		host = self.host
		user_line = "USER "+nick+' '+user+' '+host+' :'+self.realname
		nick_line = "NICK "+nick
		
		self.writeline(user_line)
		self.writeline(nick_line)
		
		# maybe this isn't such a great idea...
		LOGS = "None"
		logplugin = self.plugins.get('irclog')
		if logplugin:
			LOGS = logplugin.logfile
		else:
			rawlogplugin = self.plugins.get('rawlog')
			if logplugin:
				LOGS = rawlogplugin.logfile
		
		if self.debug:
			irc.debug(
				"#\n# CONNECTING:",
				"#       HOST: %s" % host,
				"#       USER: %s" % user_line,
				"#       NICK: %s" % nick_line,
				"#       LOGS: %s" % LOGS
			)
		
	
	
	
	#
	# IO
	#
	def io(self):
		
		# read all received text since last io;
		# might be multiple lines (or empty).
		try:
			intext = self.read()
		except SockFatal:
			raise
		
		# Handle received text.
		if intext:
			self.__handle_received_text(intext)

		#
		# PLUGINS	- - - - - - - - - - - - - - - - - - - - - - - - - - -
		#  - every now-n-then, call the plugins' `update` method
		#
		if time.time() > (self.pi_update + self.pi_interval):
			self.__handle_plugin_update()
		
		#
		# MANAGE PLUGINS - - - - - - - - - - - - - - - - - - - - - - - -
		#  - add, remove, reload plugins
		#  - do removes first (in case a plugin has been reloaded)
		#  - do adds afterward, so reloaded plugins can be re-added
		#
		if self.pm_rmv:
			self.__handle_plugin_rmv()
		
		if self.pm_add:
			self.__handle_plugin_add()
	
	
	
	#
	# PING
	#
	def ping(self, x=None):
		"""Manually send a ping (x, or current time) to the server."""
		x = x or time.time()
		self.writeline("PING :%s" % x)
	
	
	
	#
	# SHUTDOWN
	#
	def shutdown(self, msg='QUIT'):
		"""
		Send a QUIT message and shutdown the connection.
		"""
		try:
			self.writeline("QUIT %s" % msg)
			
			# this falls through to the Runner.shutdown() method
			Connect.shutdown(self)
		except SockFatal:
			pass
	
	
	
	#
	# STATUS
	#
	def status(self):
		"""Return status dict."""
		return {
			'runner' : Runner.status(self),
			'config' : self.config,
			'plugins': list(self.plugins.keys()),
			'paused' : self.__paused
			}

	
	
	
	#
	# ON MESSAGE
	#
	def on_message(self, line):
		
		e = IRCEvent(line)
		
		# if showing text (not paused)
		if self.show or self.debug:
			if self.__paused:
				self.__pwriter.write(e.line + "\r\n")
			else:
				print (e.line)
		
		# HANDLE! Let each plugin handle each event (but not PINGs)
		for pname in self.plugins:
			try:
				p = self.plugins[pname]
				p.handle(e)
			except BaseException as ex:
				msg = "Error: %s %s" % (str(type(ex)), str(ex))
				irc.debug(msg)
				p.reply(e, msg)
	
	
	
	#
	# PAUSE
	#
	def pause(self):
		"""Pause display of received lines."""
		self.__paused = True
		self.__pbuffer = trix.ncreate(
				'util.stream.buffer.Buffer', **self.ek
			)
		self.__pwriter = self.__pbuffer.writer()
	
	
	
	
	#
	# RESUME
	#
	def resume(self):
		"""
		Print any lines received while paused, the resume the previous
		mode of display.
		"""
		try:
			if self.show or self.debug:
				lines = self.__pbuffer.read().splitlines()
				for line in lines:
					print(line)
		finally:
			self.__paused = False
			self.__pbuffer = None
			self.__pwriter = None
	
	
	
	
	
	
	# ----------------------------------------------------------------
	# PLUGIN MANAGEMENT
	# ----------------------------------------------------------------
	
	def plugin_add(self, pname):
		"""Add `pname` to the plugin add-list."""
		if pname not in self.plugins:
			self.pm_add.append(pname)
	
	
	def plugin_remove(self, pname):
		"""Add `pname` to the plugin remove list."""
		if pname in self.plugins:
			self.pm_rmv.append(pname)		
	
	
	def plugin_reload(self, pname):
		"""
		Reload `pname` and add it to the plugin add and remove lists.
		"""
		try:
			reload(plugin)
			
			if pname in self.plugins:
				
				# find and reload the plugin
				ppath = self.pconfig[pname]['plugin']   # plugin class path
				pmodp = ".".join(ppath.split('.')[:-1]) # plugin module path
				pmod = trix.value(pmodp)              # plugin module object
				reload(pmod)
				
				# set the current plugin to be removed, then recreated (as 
				# the newly reloaded version) on next call to self.io();
				# NOTE: trix defines `reload()` to work in python3.
				self.pm_rmv.append(pname)
				self.pm_add.append(pname)
				
				irc.debug("plugin_reload",
						pm_rmv = self.pm_rmv,
						pm_add = self.pm_add
					)
		
		except Exception as ex:
			irc.debug (
				"plugin_reload", "DEBUG: reload fail", pname
			)
			raise
	
	
	
	
	
	# ----------------------------------------------------------------
	# PRIVATE
	# ----------------------------------------------------------------
	
	#
	# PLUGIN - LOAD
	#
	def __plugin_load(self, pname):
		"""Load plugin `pname` immediately."""
		try:
			if not (pname in self.__plugins):
				pi = self.__plugin_create(pname)
				if not pi:
					raise Exception ("plugin-create-fail", xdata(pname=pname))
				self.plugins[pname] = pi
				return pi
		except:
			irc.debug (
				"__plugin_load", "load plugin fail!", pname
			)
			raise
	
	
	
	#
	# PLUGIN - CREATE
	#
	def __plugin_create(self, pname):
		"""
		Create and return a plugin object given plugin name `pname`.
		"""
		ppath = self.pconfig[pname]['plugin'] # path for `trix.create`
		pconf = self.pconfig[pname]
		pi = trix.create(ppath, pname, self, pconf)
		if not pi:
			raise Exception ("plugin-create-fail", xdata(
					pname=pname, ppath=ppath, pconf=pconf
				))
		
		return pi
	
	
	
	#
	# PLUGIN - UNLOAD
	#
	def __plugin_unload(self, pname):
		"""Unload (delete) plugin `pname` immediately."""
		try:
			if (pname in self.plugins):
				del(self.plugins[pname])
		except:
			irc.debug ("__plugin_unload", pname)
			raise
	
	
	
	#
	# HANDLE RECEIVED LINES
	#
	def __handle_received_text(self, intext):
		
		try:
			# Wait on completed lines (crlf)...
			self.__lineq.feed(intext)
			
			# ...and handle each line.
			for line in self.__lineq.lines:
				if line[0:4] == 'PING':
					RESP = line.split()[1] # handle PING
					self.writeline('PONG ' + RESP)
				else:
					self.on_message(line)  # handle everything besides PINGs
		
		except Exception as ex:
			irc.debug (str(type(ex)), str(ex))

	
	
	#
	# HANDLE PLUGIN UPDATE
	#
	def __handle_plugin_update(self):
		
		# update to wait another `interval` seconds.
		self.pi_update = time.time()
		
		pfailed = []
		for pname in self.plugins:
			try:
				self.plugins[pname].update()
			except Exception as ex:
				if self.debug:
					irc.debug(
						"Plugin Update Failed", "Removing: %s" % pname,
						"Error: %s" % str(ex)
					)
				pfailed.append(pname)
		
		# remove plugins that failed to load
		if pfailed:
			for pname in pfailed:
				del(self.plugins[pname])
		
	
	
	#
	# HANDLE PLUGIN REMOVE
	#
	def __handle_plugin_rmv(self):
		try:
			for pname in self.pm_rmv:
				if (pname in self.pm_rmv) and (pname in self.plugins):
					del(self.plugins[pname])
					irc.debug(
						"irc_connect.__handle_plugin_rmv", "removed plugin", 
							pname
						)
		except Exception as ex:
			irc.debug ("irc_connect.__handle_plugin_rmv", 
					str(type(ex), str(ex))
				)
		finally:
			self.pm_rmv = []
	
	
	
	#
	# HANDLE PLUGIN ADD
	#
	def __handle_plugin_add(self):
		pname = None
		try:
			for pname in self.pm_add:
				if (pname in self.pm_add):
					self.plugins[pname] = self.__plugin_load(pname)
		except Exception as ex:
			irc.debug ("irc_connect.__handle_plugin_add", 
					pname=pname, addlist=self.pm_add
				)
		finally:
			self.pm_add = []

