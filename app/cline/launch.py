#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from . import *


class launch(cline):
	"""
	Launch a trix Runner in a new process.
	
	This command is used exclusively by the `trix.process()` method.
	See `trix.process()` help for information on how to run a trix
	`Runner` object (or any compatable object) in a new process using
	the "launch" command.
	"""
	def __init__(self):
		cline.__init__(self)
		try:
			# --- unpack object args and load module ---
			
			d_meth = d_dict = d_type = d_obj = None
			obj = ca = ca64 = clsname = clsargs = clskrgs = None
			methname = methargs = methkrgs = None
			
			#
			# derr - success recorder (lets you see what went right before 
			# something went wrong).
			#
			derr = {}
			
			#
			# COMPACT ARGS
			# expand the first argument, a compact b64 json (array) string
			#
			ca64 = trix.ncreate('fmt.JCompact').expand(self.args[0])
			derr['compact-args'] = ca64
			
			#
			# ALL ARGS
			# convert compressed args/krgs to an array
			#
			ca = trix.jparse(ca64.decode('UTF8'))
			derr['all-args'] = ca
			
			#
			# CLASS ARGS
			# 3 args required (for object creation)
			#  - c = class - a string fit for `trix.create`
			#  - a = args  - class constructor args...
			#  - k = kwargs  ...and kwargs
			#
			clsname,clsargs,clskrgs = ca[0:3]
			derr['class-args'] = (clsname,clsargs,clskrgs)
			
			#
			# THIS IS THE OBJECT (eg, 'net.server.Server')
			#
			obj = trix.create(clsname, *clsargs, **clskrgs)
			
			#
			# METHOD ARGS
			# Unpack method args and load module:
			#   - m  = method (of object `o`) to call
			#   - ma = method args
			#   - mk = method kwargs
			#
			methname,methargs,methkrgs = ca[3:6]
			derr['method-args'] = (methname,methargs,methkrgs)
			
			
			#
			# build and call the object's specified method
			#  - DEBUGGING: track the building of `meth`
			#
			if methname:
				
				d_obj = obj
				d_type = type(obj)
				d_dict = d_type.__dict__
				d_meth = methname
				
				# get the actuall method object as `methname`
				try:
					meth = dict(type(obj).__dict__)[methname]
				except Exception as ex:
					raise
			
				#
				# CALL THE METHOD!
				#
				meth(obj, *methargs, **methkrgs)
				
				#
				# When `meth()` exits, execution ends. Until then,
				# we're stuck in the line above (meth(obj,...)
				#
		
		except BaseException as ex:
			
			trix.log ('MAIN: BaseException', str(ex), ex.args)
			
			# group arguments for easier reading of exception
			xmeth = dict(
					methargs=methargs, methkrgs=methkrgs,
					d_meth=d_meth, d_type=d_type, d_obj=d_obj
				)
			xparams = dict(
					app=self.app, cmd=self.cmd, args=self.args, kwargs=self.kwargs, 
				)
			
			# package the exception into a dict
			errdict = dict(
				message = "err-launch-fail",
				x_args = ex.args,
				x_meth = xmeth,
				x_params = xparams,
				x_type = type(ex),
				derr = derr, 
				obj = obj,
				mapprxy = d_dict, 
				tracebk = trix.tracebk()
			)
			
			# JCompact the dict and write it to stderr as a json string
			#jc = trix.ncreate('fmt.JDisplay') # debugging
			jc = trix.ncreate('fmt.JCompact')
			sys.stderr.write(jc(errdict))
			
			trix.log ('\n\nMAIN: end BaseException')
	