#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from ..util.event import *
from ..util.runner import *
from ..util.wrap import *
from ..util.xqueue import *


SERVICES_NCONFIG = "app/config/service/en.service.conf"


#
# --------- SERVICES -----------------
#
class Services(Runner):
	"""
	Container for various services.
	
	Services warp a single object and make use of it to perform 
	actions and return results.
	
	# start services...
	from trix.app.service import *
	s = Services()
	"""
	
	# INIT
	def __init__(self, config=None, **k):
		
		config = config or trix.nconfig(SERVICES_NCONFIG)
		if not config:
			raise Exception ("Services: Config required.")
		
		Runner.__init__(self, config, **k)
		
		self.__services = {}
		
		serviceConfDict = config['services']
		for sid in serviceConfDict:
			
			# get the service config dict
			sconfig = serviceConfDict[sid]
			
			# prep for potential errors
			n_create = n_config = o_create = o_config = realconf = None
			
			# get config and create the object
			if "ncreate" in sconfig:
				n_create = sconfig['ncreate']
				n_config = sconfig.get('nconfig')
				realconf = [trix.nconfig(n_config)]
			elif "ncreate" in sconfig:
				o_create = sconfig['create']
				o_config = sconfig.get('config')
				realconf = [trix.config(o_config)]
			else:
				realconf = [serviceConfDict]
			
			# Create the object.
			try:
				sobject = trix.ncreate(n_create, *realconf)
			except Exception as ex:
				raise type(ex)(xdata(
					n_create=n_create, n_config=n_config, o_create=o_create,
					o_config=o_config, realconf=realconf, sid=sid
				))
			
			# create, store, and start the service object
			self.__services[sid] = Service(sid, sobject)
		
		#
		# Start running the Services io loop (in a thread!)
		#
		self.start()
		
	
	# SERVICES - SERVICES
	@property
	def services(self):
		return self.__services.keys()
	
	
	# SERVICES - IO
	def io(self):
		# give each service a chance to handle messages
		for s in self.__services:
			self.__services[s].handle_io()
	
	
	# SERVICES - CONNECT
	def connect(self, serviceid):
		"""
		Pass `serviceid` string. Returns a new ServiceConnect object that 
		gives access to the service's features.
		
		Pass an event object to ServiceConnect using the `request` method
		and poll `replies` to receive events in the same order as they
		were given. Check `Event.reply` (or Event.error) for the result.
		"""
		#
		# all you have to do is add a queue pair to the id'd service
		# and send the same queue pair to the connection object, then,
		# of course, call the services's `handle_io` method
		# frequently.
		#
		if not serviceid in self.__services:
			raise KeyError("No such service.", xdata(
					error="err-connect-fail", message="no-such-service",
					serviceid=serviceid
				))
			
		# Get the service we're connecting to...
		s = self.__services[serviceid]
		
		#
		# The ServiceConnect gets REAL Queues, so when they go away 
		# (eg, when the ServiceConnect object is deleted) the server 
		# will know it (because of a Reference Error) and will remove
		# the pair form its list.
		#
		realQPair = p = [Queue(), Queue()]
		
		# add the queue proxy pair to the requested Service object
		s.addqueues([trix.proxify(p[0]), trix.proxify(p[1])])
		
		# create and return a ServiceConnect object
		return ServiceConnect(s.serviceid, realQPair)
	
	



#
# --------- SERVICE IO -----------------
#
class ServiceIO(object):
	pass





#
# --------- SERVICE -----------------
#
class Service(ServiceIO):
	"""
	A single service object, which handles requests.
	
	Service objects are always started by and contained by the Services
	object. There's never a reason (or a practical use) for creating a
	Service object by calling Service(...) directly. There's no need 
	and no way to access Service objects directly. They work in the 
	background and are always accessed to a ServiceConnect object that
	is obtained by calling the `Services.connect()` method.
	
	See the ServiceConnect help for usage notes/examples.
	"""
	def __init__(self, serviceid, sobject):
		ServiceIO.__init__(self)
		
		self.__starttime = time.time()
		self.__serviceid = serviceid
		self.__object = sobject
		self.__wrapper = Wrap(sobject)
		self.__qpairs = []
	
	
	@property
	def serviceid(self):
		"""
		Return the service identifier value; the key for this object's
		value in the services configuration dict. 
		"""
		return self.__serviceid
	
	@property
	def servicetype(self):
		"""Return the type of this services' wrapped object."""
		return type(self.__object)
	
	@property
	def uptime(self):
		"""Time in seconds (float) since this services' creation."""
		return time.time() - self.__starttime
	
	
	# SERVICE - ADD QUEUES
	def addqueues(self, qproxypair):
		"""To be called by the owning Services object."""
		self.__qpairs.append(qproxypair)
	
	
	# SERVICE - HANDLE IO
	def handle_io(self):
		"""To be called only by the owning Services object."""
		
		for queues in self.__qpairs:
			try:
				qin, qout = queues
				
				# pop an event request from the Queue
				e = qin.get_nowait()
				
				# execute the command
				e.reply = self.handle_request(e)
				
				# Set the reply and return the event to the caller via the
				# out-queue (which is the client's in-queue).
				qout.put(e)
			
			except Empty:
				pass
			except ReferenceError:
				self.__qpairs.remove(queues)
			except Exception:
				e.error = xdata(qin=qin,qout=qout,e=e.dict)
				qout.put(e) # report the error!
	
	
	# SERVICE - HANDLE REQUEST
	def handle_request(self, e):
		"""Internal use only. Calls the wrapper, returns a value."""
		
		#
		# If there's no command, return a dict with information and, 
		# potentially, debugging data.
		#
		if not e.argc:
			return dict(
					service=self.serviceid, uptime=self.uptime, 
					target=repr(self.__object)
				)
				# TODO: Add wrapped object's attrs to this dict.
		
		#
		# Call the wrapped object; Return the result, or raise any
		# exceptions (to be caught in the calling method and placed in
		# the Event object's "error" property).
		#
		try:
			return self.__wrapper(*e.argv, **e.kwargs)
		except Exception as ex:
			raise type(ex) ('err-service-fail', xdata(
					message="service-request-fail", event=e.dict
				))





#
# --------- SERVICE CONNECT -----------------
#
class ServiceConnect(ServiceIO):
	"""
	Client connection to a single Service object.
	
	ServiceConnect objects communicate with Service objects by passing
	Event objects through a system of queues. Each ServiceConnect has
	its own set of queues by which requests are sent and results 
	received (as Event objects).
	
	ServiceConnect objects are obtained by calling `Services.connect`.
	There's never a reason (nor a practical use) for creating a
	ServiceConnect object directly.
	
	# EXAMPLE
	from trix.app.service import *
	s = Services()                    # Services starts automatically
	c = s.connect('irclog')           # get a service connection
	e = c.open()                      # don't forget to open the db
	e = c('addnet', "irc.Quake.net")  # two ways to call methods
	e = c.addnet("irc.undernet.org")
	e = c.getnets()                   # retrieve all network records
	e.dict                            # notice cursor in reply
	
	e = c.fetchn(e.reply)             # pass the cursor to fetchn()
	e.reply                           # get the result
	
	NOTES:
	 * ServiceConnect requests time out after 9 seconds. This default 
	   value may be changed by setting ServiceConnect.CallTimeout to
	   a different value. It may be changed per request by passing
	   keyword argument "service_connect_timeout" as a float - the 
	   number of seconds to wait before timeout.
	"""
	
	CallTimeout = 9
	
	def __init__(self, serviceid, queues):
		"""
		ServiceConnect must always be created by calling the 
		`Service.connect()` method.
		"""
		ServiceIO.__init__(self)
		
		#
		# The same queues in the opposite order; what's in for the 
		# service is out for the client (and vice versa). These are
		# the real queues - Service only holds proxies.
		#
		self.__qout, self.__qin = queues
		self.__sid = serviceid
	
	
	def __call__(self, cmd, *a, **k):
		"""
		Create and pass an event to the Service. Wait for and return the
		reply. Raise if there's an exception.
		"""
		c = Event(cmd, *a, **k)
		self.__qout.put(c)
		
		# don't let this block the program forever. Default: 9 sec
		tout = trix.kpop(k, 'service_connect_timeout')
		tout = tout.get('service_connect_timeout', self.CallTimeout)
		tin = time.time()
		
		# loop until result (or timeout)
		r = None
		while not r:
			try:
				r = self.__qin.get_nowait()
				if r:
					return r
				time.sleep(0.01)
			except Empty:
				if time.time() - tin > tout:
					raise Exception("ServiceConnect Timeout", tout)
	
	
	def __getattr__(self, name):
		"""
		Return an object that will call `name` method via `__call__()`.
		This allows `ServiceConnect` to wrap cross-thread calls to the
		object wrapped by `Service()` when they're given in the manner
		of a typical python method call.
		
		>>> from trix.app.service import *
		>>> ss = Services()
		>>> db = ss.connect('irclog')
		>>> db.addnet("irc.undernet.eu")
		>>> ev = db.getnets()
		>>> ev.reply
		"""
		return SCCaller(self, name)
	


#
# Utility
#
class SCCaller(object):

	def __init__(self, scobject, name):
		self.__obj = scobject
		self.__name = name
	
	def __call__(self, *a, **k):
		return self.__obj(self.__name, *a, **k)



