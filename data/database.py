#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
# 


from .. import *


class Database(object):
	"""Wrapper for DB-API 2.0 database access."""
	
	
	@classmethod
	def fetchn(cls, cursor, n=None):
		"""
		This classmethod returns a list of `n` number of rows from 
		`cursor`, starting at its current position. If value is None, 
		all rows are returned.
		"""
		if n == None:
			return cursor.fetchall()
		else:
			r = []
			while n > 0:
				r.append(cursor.fetchone())
			return r
	
	
	
	def __init__(self, conf=None, *a, **k):
		"""
		Pass config dict `conf` and/or kwargs with keys:
		 - module: a db-api-2 module or module name (default: "sqlite3")
		 - args  : arguments to be passed to the open() method.
		 - path  : file path to the db file (if applicable); if included,
		           this value is prepended to args.
		 - auto  : Bool; auto-init blank database if True.
		 - sql   : If auto is True, a config key "sql" must also exist 
		           with a dict value containing a "create" key with a 
		           list of sql statements that define the structure of
		           the database. This dict may also contain an "op" key
		           with a dict containing named sql queries that will be
		           triggered by the `Database.opq` and `Database.ops`
		           methods.
		
		Alternately, `config` may be a file-based database's path with
		optional kwargs specifying the other params.
		"""
		
		# path might be None for some DBMS
		path = None
		
		# store args for opening database
		self.__args = a
		
		if 'nconfig' in k:
			conf = trix.nconfig(k['nconfig'])
		elif 'config' in k:
			conf = trix.config(k['config'])
		
		# get the configuration
		conf = conf or {}
		try:
			conf.update(k)
			"""
			# this was a mistake.. some dbms don't require a path
			if not 'path' in conf:
				raise ValueError('db-init-fail', xdata(detail='path-required',
						reason='db-path-required', config=conf, k=k, a=a
					))
			"""
			path = conf.get('path')
		
		except AttributeError:
			# if config is not a dict, it must be a db file path
			path = conf
			conf = {}
			conf.update(k)
		
		#
		# PATH
		#  - Some databases need a `path`, some don't.
		#  - If there's a path, insert it as the first item in args.
		#  - If there's a path, expand it to a full path and make sure its
		#    containing directory exists.
		#  - In any case, store the given path.
		#
		if path:
			path = trix.path(path, affirm='makepath').path
			a = list(a)
			a.insert(0, path)
		
		# store path; Might be None for some dbms.
		self.__path = path
		
		# store args
		self.__args = a
		
		# store configuration
		self.__config = conf
		
		# init runtime values
		self.__con = None
		self.__inited = None
		
		#
		# MODULE
		#  - module may be given by name or by passing the actual module
		#
		mod = conf.get('module', 'sqlite3')
		try:
			self.__mod = trix.module(mod)
			self.__modname = mod
		except:
			self.__mod = mod
			self.__modname = type(self.__mod).__name__
		
		#
		# SQL
		#
		sql = conf.get('sql', {})
		try:
			# string path to sql file
			rdr = trix.path(sql).reader()
			sql = trix.jparse(rdr.read())
		except:
			sql = sql
		
		# sql/op
		self.__sql = conf.get('sql', {})
		self.__op = self.__sql.get('op', {})
		
		#
		# AUTO-INIT
		#  - If autoinit is set to true, the first call to open will try
		#    to create the new database by executing the queries defined
		#    in the `sql` parameter's content.
		#  - An `sql` value must exist, or autoinit will remain False.
		#
		self.__autoinit =  self.__sql and conf.get('auto', False)
	
	
	
	def __del__(self):
		"""Close this database if open."""
		try:
			self.close()
		except:
			pass	
	
	
	
	@property
	def active (self):
		"""True if the database is open/connected."""
		return True if self.__con else False
	
	@property
	def config (self):
		"""True if the database is open/connected."""
		return self.__config
	
	@property
	def con (self):
		"""Return the DB connection object."""
		return self.__con
	
	@property
	def mod (self):
		"""Return the DB module object."""
		return self.__mod
	
	@property
	def modname (self):
		"""Return the DB module name."""
		return self.__modname
	
	@property
	def path (self):
		"""Return the DB module name. (It may be None for some DBMS.)"""
		return self.__path
	
	@property
	def sql(self):
		"""Return the full config sql dict."""
		return self.__sql
	
	@property
	def sop(self):
		"""Return the preconfigured SQL Operations dict `op`."""
		return self.__op
	
	
	# CAT
	def cat(self, cat):
		"""
		Returns the named SQL query category as a list or a dict as 
		defined in configuration: Queries in the 'create' category are
		list; those in 'op' are dict.
		"""
		return self.__sql[cat]
		
	
	# CREATE
	def create(self):
		"""
		Initialize database using the "create" category of the sql dict
		defined in config. This category is a list of sql statements
		intended to define tables and indices, and to populate tables
		if needed. Also creates a __corectl table with one field whose
		value is set to the current __corectl version, 3.
		"""
		cr = self.cat("create")
		if cr:
			self.qlist(cr)
		
		self.query("create table __meta (k,v)")
		self.query("insert into __meta values ('version', 3)")
		self.commit()
	
	
	# OPEN
	def open(self, **k):
		"""
		Open database using preconfigured arguments and optional kwargs.
		"""
		if self.active:
			raise Exception('db-open-fail', xdata(reason='already-open'))
		elif not self.mod:
			raise Exception('db-open-fail', xdata(
					reason='module-not-specified'
				))
		
		try:
			self.__con = self.mod.connect(*self.__args, **k)
		except BaseException as ex:
			raise type(ex)('db-open-fail', self.xdata(
				python=str(ex), args=self.__args, kwargs=k
			))
		
		# auto-init
		if not self.__autoinit:
			self.__inited = True
		elif not self.__inited:
			try:
				cc = self.query('select v from __meta where k="version"')
				self.__inited = True if cc.fetchone() else False
			except Exception as ex:
				self.create()
				cc = self.query('select v from __meta where k="version"')
				self.__inited = True if cc.fetchone() else False
				if not self.__inited:
					raise Exception('db-autoinit', self.xdata())
			finally:
				self.__autoinit = False
	
	# opens (open, return self)
	def opens(self, **k):
		"""Open database connection; return self."""
		self.open(**k)
		return self
	
	
	# CLOSE
	def close(self):
		"""Close the database connection."""
		try:
			if self.__con and self.active:
				self.__con.close()
		finally:
			self.__con = None
	
	
	
	# EXEC
	def execute(self, *a):
		"""Execute a query with given args. Returns a cursor."""
		return self.__con.execute(*a)
	
	def executemany(self, *a):
		"""Execute multiple queries with given args. Returns a cursor."""
		return self.__con.executemany(*a)
	
	def cursor(self):
		"""Returns a cursor."""
		return self.__con.cursor()
	
	def commit(self):
		"""
		Commit a transaction.
		
		IMPORTANT:
		The calling code is responsible for commiting transactions. If
		you're running insert queries and they're not showing up, you
		should look through your code to make sure db.commit() is being
		called at all the appropriate places.
		"""
		self.__con.commit()
	
	def rollback(self):
		"""Rollback a transaction."""
		self.__con.rollback()
	
	
	# ERROR ROLLBACK
	def __rollback(self):
		#
		#Used only in except clauses, in case the database was not open
		#(or some other error not related to the sql itself). This keeps
		#the wrong error from being raised.
		#
		try:
			self.rollback()
		except:
			pass
	
	
	#
	# OPERATIONS
	#  - handle queries defined in the 'sql' config.
	#
	
	# QUERY
	def query(self, sql, *a):
		"""
		Execute query with given args; Rollback on error.
		
		On success, the calling code must commit (if/when appropriate).
		"""
		try:
			return self.execute(sql, *a)
		except Exception as ex:
			if not self.active:
				raise Exception('db-inactive', self.xdata())
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql))
	
	# Q-MANY
	def qmany(self, sql, *a):
		"""
		Just like `self.query`, but uses executemany.
		
		On success, the calling code must commit (if/when appropriate).
		"""
		try:
			return self.executemany(sql, *a)
		except Exception:
			if not self.active:
				raise Exception('db-inactive', self.xdata())
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql, args=a))
	
	# Q-LIST
	def qlist(self, queries, cursor=None):
		"""
		Execute list of query strings. On error, rollback.
		
		On success, the calling code must commit (if/when appropriate).
		"""
		try:
			cc = cursor if cursor else self.cursor()
			qn=0
			for sql in queries:
				cc.execute(sql)
				qn += 1
			return cc
		except Exception as ex:
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql, qitem=qn,
				qlist=queries
			))
	
	
	# OPQ - Op Query
	def opq (self, qname, *a):
		"""
		Pass query name as defined in config in the 'op' section, and 
		any arguments required by the query; Executes the query and 
		returns a cursor.
		
		On success, your code must do the commit (if/when appropriate).
		"""
		return self.query(self.__op[qname], *a)
	
	
	# OPS - Op Query List
	def ops (self, qname, *a):
		"""
		Execute a list of queries specified by an op name. This only 
		applies to op values that are lists of queries to execute.
		On error, rollback.
		
		On success, your code must do the commit (if/when appropriate).
		"""
		#
		# Transaction opening is automatic so if there's an exception,
		# self.query() will do the rollback for all.
		#
		# I guess it's best to stick to the principle that the caller 
		# always does the commit. I need to document that and post some
		# reminders in comments everywhere it's necessary.
		#
		try:
			xq = len(self.__op[qname])
			xa = len(a)
			xsql = self.__op[qname]
			for i in range(0, xq):
				sql = xsql[i]
				if (i<xa) and (a[i]):
					self.query(sql, a[i])
				else:
					self.query(sql)
		except:
			raise Exception(self.xdata(qname=qname, args=a))
	
	
	def xdata(self, **k):
		"""Return a dict containing debug information."""
		d = dict(dbmodule=self.__modname, dbactive=self.active)
		if self.path:
			d['path'] = self.path
		return xdata(d, **k)


