#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .connect import Connect
from ..util.runner import *
from ..util.sock.sockwrap import SockFatal, SockError

class Client(Runner):
	"""Client with multiple connections."""
	
	DefType = Connect
	
	
	# INIT
	def __init__(self, config=None, **k):
		"""Pass config for Runner."""
		Runner.__init__(self, config, **k)
		self.__connections = {}
		self.__removelist = []
		self.__keepalive = self.config.get('keepalive', False)
	
	
	# DEL
	def __del__(self):
		"""Calls `Stop()`."""
		try:
			self.stop()
		except:
			pass
	
	
	
	@property
	def conlist(self):
		"""Return list of of connection names."""
		return list(self.__connections.keys())
	
	@property
	def connections(self):
		"""Return dict containing connection objects."""
		return self.__connections
	
	@property
	def keepalive(self):
		"""Return 'keepalive' value provided to constructor."""
		return self.__keepalive
	
	
	# CONTAINS
	def __contains__(self, connid):
		"""Return True if connid in this Client's connection list."""
		return connid in self.__connections
	
	
	# GET ITEM
	def __getitem__(self, connid):
		"""Return named connection."""
		return self.__connections[connid]
	
	
	
	# DISCONNECT
	def disconnect(self, **connid):
		"""Pass one or more `connid` connection names for removal."""
		self.remove(connid)
	
	
	# CONNECT
	def connect(self, connid, config=None, **k):
		"""
		Pass string `connid`, a unique name for this connection. Also 
		pass optional `config` dict (which is, as always, updated by 
		kwargs). 
		
		Config (or kwargs) should contain a "create" or "ncreate" key 
		describing the full (or inner, repsectively) pythonic path to 
		the [package.][module.]class to be created. This object must 
		implement the Config class (which is based on Runner).
		
		If no "create" or "ncreate" class path string is specified, the
		default trix.net.connect.Connect is used.
		
		Creates the described connection object and adds it to the 
		`self.conlist` connection list property.
		"""
		xt=xa=xd = None
		config = config or {}
		try:
			
			# this allows dict config
			config.update(k)
			if 'create' in config:
				T = trix.value(config['connect'])
			elif 'ncreate' in config:
				T = trix.nvalue(config['nconnect'])
			else:
				T = self.DefType #Connect
		except Exception as ex:
			T = self.DefType 
			xt = type(ex)
			xa = ex.args
			xd = xdata()
		
		
		# this allows a config other than type dict (eg, port number)
		try:
			# add connid to the connection's config
			config.setdefault('connid', connid)
			
			connection = T(config)
			self.__connections[connid] = connection
		except Exception as ex:
			raise type(ex)('err-connect-fail', xdata(
				xprior=[xt,xa,xd], T=T #, config=config
			))			
	
	
	# IO
	def io(self):
		"""Check for (and handle) input for each connection."""
		
		condict = self.__connections
		if condict:
			
			# Handle any removals before processing the list
			rmvlist = self.__removelist
			if rmvlist:
				self.remove(rmvlist)
			
			# loop through each connection name 
			conkeys = list(condict.keys())
			for connid in conkeys:
				try:
					try:
						#
						# If the connection exists, handle it's io. Otherwise, 
						# remove it.
						#
						conn = condict.get(connid)
						if conn:
							self.handleio(conn)
						else:
							rmvlist.append(connid)
					
					# if there's a fatal socket error, mark
					except SockFatal as ex:
						rmvlist.append(connid)
						raise type(ex)("sock-fatal-err", xdata())
				
				except Exception as ex:
					self.handlex(connid, type(ex), ex.args, xdata())
	
	
	# STOP
	def stop(self):
		"""Stop the client. Remove/shutdown all connections."""
		Runner.stop(self)
		self.remove(list(self.__connections.keys()))

	
	# REMOVE (connections)
	def remove(self, rmvlist):
		"""
		Remove any connections with `connid` matching an item in rmvlist.
		Connection `shutdown()` method is called, then deleted from the
		list. Any exceptions are ignored.
		
		When the list is empty, this Client will stop running unless the
		`self.keepalive` property is True.
		"""
		for cname in rmvlist:
			conn = self.__connections.get(cname)
			if conn:
				try:
					conn.shutdown()
				except:
					pass
				
				try:
					if cname in self.__connections:
						del(self.__connections[cname])
				except:
					pass
		
		# should we stop running?
		if (not self.__connections) and (not self.__keepalive):
			Runner.stop(self)
	
	
	# --- override these to handle input and exceptions ---
	
	# HANDLE-DATA
	def handleio(self, conn):
		"""
		Default handling of input/output. Reads received content into a
		buffer and then prints it in the terminal window.
		
		Subclasses should override this method to deal with received 
		data in whatever way is appropriate to their purpose.
		"""
		try:
			x = conn.read()
			if x:
				print (x)
		except SockFatal as ex:
			self.__removelist.append(conn)
	
	
	# HANDLE-X (Exception)
	def handlex(self, connid, xtype, xargs, xdata):
		"""
		Default handling of errors. Displays exception and "xdata" in 
		the terminal window.
		
		Subclasses should override this method to deal with exceptions 
		in whatever way is appropriate to the context in which they're
		running.
		"""
		print ("\nEXCEPTION! %s: %s(%s)" % (connid, xtype, xargs))
		if xdata:
			trix.display(xdata)
	

