#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import * # trix, sys
from ..fmt import JCompact
from .runner import Runner
from .xqueue import *
import subprocess


class ProcessError(Exception): pass
class LaunchError(ProcessError): pass
try:
	Timeout = subprocess.Timeout
except:
	Timeout = Exception


PROC_IO_TIMEOUT = 0.01


#
# CPORT CAN'T BE AN ARGUMENT
#  - All Process instances try to get the remote process to create
#    a connection, then timeout if they don't cooperate.
#  - However... if a "ctime" kwarg is provided, it overrides the 
#    default timeout (5 minutes), and if it's set to zero, no attempt
#    to receive a connection.
#

class Process(Runner):
	"""
	1 - Create a process given object creation args.
	2 - Launch the process (giving `run` args as needed)
	3 - Start this Process object...
	  - loop waiting for input/error; errors that fall through (from the
	    remote process) will come via stderr and are fatal. Errors from
	    the control handler may be handled as appropriate.
	4 - Read and handle data received via qread (for stdin) and/or cread
	    (for data received via the process server).
	"""
	
	CLINE = "%s -m %s launch %s"
	CTIME = 300 # timeout for socket connect-back: default 5m
	CTOUT = 3.0 # timeout for cport communication response 3s
	DEBUG = {}
	HAND = trix.innerpath('net.handler.hlines.HandleLines')
	WRAP = trix.innerpath('util.sock.sockwrap.sockwrap')
	ENCODE = DEF_ENCODE
	
	#
	# INIT
	#
	def __init__(self, cpath, *a, **k):
		"""
		Pass 'package.module.Class' as `cpath`, plus any args/kwargs for 
		creation of the object to run in a remote process.
		
		Encoding-related kwargs ('encoding' and 'errors') are shared with
		both the remote process and this controlling Process object, which
		must communicate by bytes encoded with the specified encoding (or 
		DEF_ENCODE).
		
		Note that the remote process Runner will also react to the same 
		kwargs as this Process object (in this local process), so their 
		"sleep" time will be in synch.
		"""
		
		rk = trix.kpop(k, 'encoding errors sleep')
		
		# DEBUG INFO
		ID = "%s.%s:%i" % (__name__, type(self).__name__, trix.pid())
		#trix.log("%s.%s:%i" % (__name__, type(self).__name__, trix.pid()))
		processconfig = dict(ID=ID, cpath=cpath, a=a, k=k)
		
		#
		# DEFAULT ENCODING
		#  - An encoding is necessary, and defaults to DEF_ENCODE. This
		#    encoding's used to convert bytes sent from the remote process
		#    via pipes (using the EncodingHelper's `encode` and `decode`
		#    methods).
		#  - If your system is producing bytes in an encoding other than
		#    DEF_ENCODE, set Process.ENCODE to that encoding.
		#  - If encoding-related errors arise, it may be necessary to
		#    add some (more) complication to this class or to __main__. 
		#    For now, keep fingers crossed.
		#
		k = dict(encoding=self.ENCODE)
		
		#
		# RUNNER KWARGS
		#  - The 'encoding', 'errorse, and 'sleep' kwargs, extracted to
		#    `rk`, above, are shared in common with the remote process.
		#
		Runner.__init__(self, processconfig=processconfig, **rk)
		
		#
		# LAUNCH PARAMS
		#  - These (cpath,a,k) must be sent to the launch method
		#
		self.__cpath = cpath # object path (package.module.class/function)
		self.__args = a      # object constructor args
		self.__krgs = k      # object constructor kwargs
		
		#
		# PIPES
		#  - Pipes are used after launch to receive any launch errors;
		#  - The stdin pipe is never needed by the trix package, but is
		#    available in case needed for the launching of some externally
		#    defined object.
		#
		self.__p = None
		self.__pk = {}   # kwargs for Popen constructor
		#self.__pk.setdefault('stdin', subprocess.PIPE)
		self.__pk.setdefault('stdout', subprocess.PIPE) 
		self.__pk.setdefault('stderr', subprocess.PIPE) 
		
		#
		# STDOUT QUEUE
		#  - Data recieved from stdin is queued. Use self.reado to pop
		#    one item (or `None` if no item exists).
		#  - Anything received from stderr is converted to a ProcessError
		#    or LaunchError exception and raised immediately.
		#
		self.__stdrecv = Queue()
		
		#
		# CONTROL SERVER
		#  - Pass a cport kwarg if you want communication between this
		#    object and the remote process.
		#  - Launch a server and wait (until timeout) for the remote 
		#    process to connect.
		# 
		self.__cserv = None
		self.__csock = None
		self.__chand = None
		self.__cport = None
		self.__ctime = k.get('ctime', self.CTIME)
		self.__qsend = Queue()
		
		# This should only be set after `launch()` is called.
		#self.__ctimeout = None
		
		# keep an eye on self.stop() for a while
		self.__stoplog = []
		self.__exitcode = None
		
		#
		# DEBUGGING
		#  - store process-id and constructor params
		#
		#self.dbg = dict(pid=trix.pid(), dak=dict(cpath=cpath, a=a, k=k))
		#trix.log("process.dbg", self.dbg)
	
	
	
	#
	# DEL
	#
	def __del__(self):
		if self.active:
			self.stop()
	
	
	# runtime values
	
	@property
	def args(self):
		"""Additional Process constructor args."""
		return self.__args
	
	@property
	def kwargs(self):
		"""Process constructor kwargs."""
		return self.__krgs
	
	@property
	def cpath(self):
		"""module.class path (1st Process constructor arg)."""
		return self.__cpath
	
	@property
	def cport(self):
		"""Remote process connection port."""
		return self.__cport
	
	@property
	def csock(self):
		"""Remote process connection socket."""
		return self.__csock
	
	@property
	def chand(self):
		"""Remote process connection handler."""
		return self.__chand
	
	@property
	def ctime(self):
		"""Time limit for remote process to connect. Default: 5 min."""
		return self.__ctime
	
	
	
	# runtime values
	
	@property
	def active(self):
		"""True if the process exists and has not exited."""
		try:
			return self.__p and (self.poll() == None)
		except:
			return False
	
	@property
	def pid(self):
		"""Return the remote process id."""
		return self.__p.pid if self.__p else None
	
	@property
	def p(self):
		"""Direct access to the `subprocess.Popen` object."""
		return self.__p
	
	
	
	
	
	def poll(self):
		"""
		Poll for an exit code; Remains None until the process terminates.
		Retains the value even after the process is terminated - even 
		after self.__p is deleted.
		"""
		try:
			try:
				return self.__poll
			except:
				poll = self.__p.poll()
				if poll != None:
					self.__poll = poll
					return self.__poll
				else:
					return None
		except:
			return None
	
	
	
	
	
	#
	# STATUS/DISPLAY
	#
	def status(self):
		"""Return the status of this object."""
		runner = Runner.status(self)
		process = dict(
			active = self.active,
			cpath = self.__cpath,
			cport = self.__cport,
			chand = self.__chand,
			poll = self.poll(),
			pid = self.pid
		)
		
		# add the exit code, if one exists
		if self.__stoplog != None:
			process['stoplog'] = self.__stoplog
		
		return dict(
			runner = runner,
			process = process
		)
	
	
	# DISPLAY
	def display(self, data=None, **k):
		"""Print formatted display of this object's status."""
		trix.display(data or self.status())
	
	
	# REMOTE STATUS
	def rstatus(self):
		"""Return the remote process status as a dict."""
		self.write('status\r\n')
		tstart = time.time()
		tmout = tstart+self.CTOUT
		while time.time() < tmout:
			status = self.read().strip()
			if status:
				return trix.jparse(status)
	
	
	# REMOTE DISPLAY
	def rdisplay(self):
		"""Display the remote process status in JSON format."""
		trix.display(self.rstatus())
	
	
	
	#
	#  IO - main loop handler (see `runner.Runner`)
	#
	def io(self):
		"""Manage process activity, including i/o from pipes and cserv."""
		
		# if the process dies, stop running
		if (not self.__p) or self.poll():
			self.stop()
		
		else:
			# 1 - HANDLE STDERR/STDOUT FROM REMOTE PROCESS
			self.__stdeo()
			
			# 2 - DEAL WITH CONNECTION SERVER OPERATION
			if self.__chand:
				#
				# UNDER CONSTRUCTION
				#  - Nothing to do at the moment - io is performed using
				#    the read() and write() methods.
				#  - Future releases may add maintenaince features (eg, a
				#    PING/PONG feature) here.
				#  - Either way, this `if` is still needed - if only to 
				#    prevent checking the conditions below.
				#
				pass
			
			elif self.__cserv:
				
				# Check for timeout.
				if (time.time() < self.__ctimeout):
					
					# Accept, if incoming connection is attempted.
					h = self.__cserv.acceptif()
					
					# got a connection; wrap sock and set `chand`
					if h:
						self.__csock = trix.create(self.WRAP, h[0])
						self.__chand = trix.create(self.HAND, h[0])
						self.__cserv.shutdown()
						self.__cserv = None
						
						# read pid
						time.sleep(0.01)
						rdata = self.readline()
						if rdata:
							self.receivedPid = rdata.strip()
							if not int(self.receivedPid) == self.pid:
								raise Exception("err-process-fail", xdata(
									reason="err-pid-mismatch"
								))
						
						#
						# 1 - Set self.__write to the real `_write` method.
						# 2 - Send any data that was written (and queued) before 
						#     csock and chand came online...
						#
						self.__write = self._write
						try:
							dk = self.__qsend.get_nowait()
							while dk:
								self.writeline(dk[0], **dk[1])
								dk = self.__qsend.get_nowait()
						except Empty:
							pass
				
				else:
					#
					# The timeout has been reached; stop waiting for connection
					# from the remote process.
					#
					self.__cserv.shutdown()
					self.__cserv = None
	
	
	
	
	
	#
	#
	#  STOP  
	#
	#
	def stop(self):
		"""Shutdown, terminate, or kill the process."""
		
		##
		## Send 'shutdown' command and wait for remote process to exit.
		##
		self.__stoplog.extend(['stoplog', time.time()])#
		if self.active:
			
			self.__chand.write('shutdown\r\n')
			self.__stoplog.append('shutdown sent')#
			
			# wait for process to exit
			if self.__p:
				tstart = time.time()
				tmout = tstart+1.1
				while time.time() < tmout:
					self.__exitcode = self.poll()
					if self.__exitcode == None:
						time.sleep(0.05)
					else:
						self.__exitcode = poll = self.poll()
						time.sleep(0.05)
						self.__stoplog.extend([
								'shutdown success', time.time(), "poll=%s"%str(poll),
								'active="%s"' % str(self.active)
							])#
						break
			
			#
			# CHECK PROCESS ENDED
			#  - If remote process failed to exit naturally (by 'shutdown'
			#    command), try to terminate it, or kill it if necessary.
			#
			if self.active:
				self.__stoplog.extend(['still active; terminate',
						"poll=%s"%str(self.poll())
					])#
				try:
					# TERMINATE
					self.__p.terminate()
					self.__stoplog.append("process-terminated")#
				except Exception as ex:
					self.__stoplog.append("terminate failed", type(ex), ex.args)
					try:
						# KILL
						self.__p.kill()
						self.__stoplog.append("process killed")#
					except Exception as ex:
						# TERMINATE/KILL FAIL
						self.__stoplog.append("kill failed", type(ex), ex.args)#
			
			# Clean up; 
			try:
				# record any exit error
				self.__exitcode = self.poll()
				
				# make sure p is garbage-collected
				self.__p = None
				
			except Exception as ex:
				self.__stoplog.append("cleanup error", type(ex), ex.args)
			
			finally:
				# stop the runner
				Runner.stop(self)
	
	
	
	
	
	#
	# CONTROL-SOCKET I/0
	#  - copy the socket reading/writing features
	#
	def read(self, **k):
		"""Read data from control socket."""
		if self.__csock and self.__chand:
			data = self.__csock.read()
			if data:
				self.__chand.handledata(data)
			return self.__chand.read()
	
	
	def readline(self):
		"""Read a line from control socket."""
		if self.__csock and self.__chand:
			data = self.__csock.read()
			if data:
				self.__chand.handledata(data)
			return self.__chand.readline()
	
	
	def readlines(self):
		"""Read all complete lines from control socket."""
		if self.__csock and self.__chand:
			data = self.__csock.read()
			if data:
				self.__chand.handledata(data)
			return self.__chand.readlines()
	
	
	
	
	
	@property
	def write(self):
		"""
		Returns the `write` method suitable to current circumstances.
		Call this as though it were the actual `write` method.
		>>> p.write(someData)
		"""
		try:
			return self.__write
		except AttributeError:
			return self.__writeq
	
	
	def writeline(self, data, **k):
		"""Append CRLF to data and write."""
		self.write(data+"\r\n", **k)
	
	
	def _write(self, data, **k):
		"""Write data to socket."""
		if self.__csock and self.__chand:
			self.__csock.write(data, **k)
	
	
	def __writeq(self, data, **k):
		"""Queue data/k for writing when csock and chand are set."""
		self.__qsend.put([data, k])
	
	
	
	
	
	# direct send/recv methods
	
	def recv(self, sz):
		"""Standard, old-fashioned `recv` direct from socket."""
		return self.__csock.recv(sz)
	
	def send(self, data):
		"""Standard, old-fashioned `send` direct to socket."""
		return self.__csock.send(data)
	
	
	
	
	
	#
	# READ-O (Standard Output Queue)
	#
	def reado(self):
		"""Read queued standard input from remote process."""
		#
		# This has actually never happened. I'm not sure it even *can* 
		# happen.
		#
		# It may be best to remove this method.
		#
		try:
			return self.__stdrecv.get_nowait()
		except Empty:
			return None
	
	
	
	
	
	#
	# LAUNCH
	#
	def launch(self, run=None, *a, **k):
		"""
		The `run` argument may be specified if the object created (as 
		specified by the constructor args/kwargs) contains a function or
		method that must be called after the process starts. In such a 
		case, any required args/kwargs may be passed, too. If the object
		is a class with a constructor that starts the process, then `run`
		should be left as None and no args/kwargs may be specified.
		
		Returns `self`.
		"""
		
		if self.__p:
			raise Exception('err-launch-fail', xdata(
					detail="process-already-launched", p=self.__p,
					DEBUG="Launch may be called only once per Process"
				))
		
		#
		# LAUNCH PROCESS
		#  - PROCESS  : create control server, add cport to kwargs
		#  - PROCESS  : pack args and popen()
		#  - __MAIN__ : unpack object args and load module
		#  - __MAIN__ : unpack method args
		#  - __MAIN__ : call method (eg, "run")
		#  - PROCESS  : self.start(), and return self
		#
		
		#
		# CONTROL SERVER
		#
		if self.__ctime:
			# always use the basic socserv class here
			self.__cserv = trix.ncreate('util.sock.sockserv.sockserv', 0)
			self.__cport = self.__cserv.port
		
		
		# timeout interval starts when the process launches
		self.__ctimeout = self.__ctime + time.time()
		
		
		#
		# PACK ARGS
		#
		
		# set connect-back cport
		if self.__cport:
			self.__krgs['CPORT'] = self.__cport
		
		# create a compact (json -> zlib -> base64) argument spec
		cargs = [self.__cpath, self.__args, self.__krgs, run, a, k]
		
		# compress (zlib) the json and b64 it
		clarg = JCompact().compact(cargs)
		
		# launch args
		pyexe = sys.executable
		trixp = trix.innerpath()
		fsenc = sys.getfilesystemencoding()
		cline = self.CLINE % (pyexe, trixp, clarg.decode(fsenc))
		
		
		# DEBUG
		#dbg = dict(pyexe=pyexe, trixp=trixp, fsenc=fsenc, cline=cline )
		#self.dbg['launch']=dbg
		
		
		#
		# LAUNCH REMOTE PROCESS
		#  - Popen through trix.__main__.py
		#  - The 'launch' command (in __main__) uses trix.popen(), so 
		#    stderr/stdout are set to PIPE.
		#  - Only the command line argument and kwargs are sent to popen -
		#    the `run`, `a`, and `k` values are used (in __main__) to get
		#    the external object going (eg, by calling its `run` method.)
		#
		self.__p = trix.popen(cline.split(), **self.__pk)
		
		# Give the remote process a chance to get going.
		time.sleep(0.05)
		
		# QUICK CHECK FOR LAUNCH ERRORS
		if (not self.__p) or self.poll():
			self.__stdeo(LaunchError)
		
		#
		# START PROCESS
		#  - start a thread that loops through this object's `io` method 
		#
		if not self.running:
			self.start()
		
		# return `self` so that `p=trix.process(x).launch(y)` will work.
		return self
	
	
	
	
	
	def __stdeo(self, TException=None):
		#
		# STDOUT/STDERR
		#  - queue any stdout/stderr data; raise any errors.
		#
		e=None
		o=None
		try:
			o,e = self.p.communicate(timeout=PROC_IO_TIMEOUT)
		except Timeout:
			pass
		
		# check for errors
		if e:
			# there's been an error
			TException = TException or ProcessError
			
			o = self.decode(o)
			e = self.decode(e).strip()
			
			# defaults
			XDATA = dict(stderr=e, stdout=o)
			
			if o and e:
				#
				# O AND E
				#  - If both out and err exist, an exception was raised; out
				#    is the exception message and err is the traceback.
				#  - split out into lines and parse all but the first (which
				#    is the <Exception type>).
				#
				lines = o.strip().splitlines()
				xtype = lines[0]
				xtext = "\n".join(lines[1:-1]) # last line is "Traceback:"
				
				
				# JPARSE STDOUT (o)
				try:
					_err = trix.jparse(xtext)
					XDATA['stdout'] = _err
				except Exception as ex:
					#
					# J-PARSE EXCEPTION
					#
					XDATA['xinfo'] = dict(
						message = 'stdout-parse-fail',
						xtype = type(ex),
						xargs = ex.args,
					)
				
				# TRACEBACK IS STDERR (e)
				XDATA['stderr'] = e.splitlines()

				# raise the stderr error
				raise TException('process-error', dict(
					xtype   = xtype,
					xdata   = XDATA['stdout'],
					tracebk = XDATA['stderr']
				))
				
			else:
				#
				# STDERR ONLY
				#  - otherwise, err is probably an error message string.
				#
				
				# parse the error
				try:
					_err = trix.jparse(e)
					XDATA['stderr'] = _err
				except Exception as ex:
					#
					# J-PARSE EXCEPTION
					#  - The `e` value couldn't be parsed, so let it remain as a
					#    string. Include the parse-error type and args for
					#    debugging parse errors.
					#
					XDATA['xinfo'] = dict(
						message = 'stderr-parse-fail',
						xtype = type(ex),
						xargs = ex.args
					)
			
				# raise the stderr error
				raise TException('process-error', XDATA)
		
		elif o:
			#
			# STDOUT ONLY
			#  - Some data was written. Store it in the stdrecv queue.
			#  - Read it by calling the `reado()` method.
			#
			self.__stdrecv.put(self.decode(o))
			#print ("\n#\n# RECV'D: %s\n#\n", self.decode(o))#debug
		



