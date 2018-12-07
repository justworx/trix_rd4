#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from . import *
from ...util.matheval import *
from ...util.compenc import *
from ...util.convert import *


class Calc(Plugin):
	"""
	Calculate math expressions/temperature conversions; Encode/decode
	b64/32/16.
	"""
	
	#
	# HANDLE
	#
	def handle(self, e):
		
		# --- process the command ---
		cmd = e.argvl[0]
		try:
			# If there's no command, it's an empty line, so just return.
			if not cmd.strip():
				return
		except AttributeError:
			#
			# If the first argument's not a string, it could be an int or
			# float, which would indicate this is a math equation to be
			# resolved.
			#
			self.reply(e, self.__calc(e))
			
			# Either the command is invalid (AttributeError) or it's an
			# equation that's been solved by __calc (and even if that
			# raised an error, it should be ignored. Either way, the
			# there's no need to proceed with the rest of this, so return
			# immediately regardless of the solution/error.
			return
		
		#
		# If we got this far, the command is a string, so handle it 
		# normally - the old-fashioned way - with all args being string.
		#
		try:
			# make a list of arguments as type str
			args = []
			for a in e.argvl:
				args.append(str(a))
		
			
			# MATH
			if cmd in ['calc', 'calculate']:
				#
				# In this case, the command "calc" has been issued explicitly
				# so we definitely must raise any errors in calculation.
				#
				try:
					self.reply(e, str(matheval(' '.join(args[1:]))))
				except BaseException as ex:
					self.error(
							e, type=type(ex), error=str(ex), tb=trix.tracebk(),
							xdata=xdata()
						)
				
				#
				# AND... weird as it may seem, the next "if" clause must not
				#        be "elif"... I forgot why, but if you care enough,
				#        just go right ahead and trace through the code to
				#        figure out why.
				#
				return
			
			
			# CONVERT
			if self.__istempc(cmd):
				try:
					ctemp = Convert().temp(cmd[2], cmd[0], float(e.argv[1]))
					self.reply(e, str(ctemp)+cmd[2].upper())
					return
				except:
					pass
			
			
			# BASE-64/32/16
			enc = self.owner.encoding
			try:
				if (cmd[0]=='b') and (cmd[1] in "631"):
					
					#
					# These must be case-sensitive. Non-strings will cause
					# an exception!
					#
					spx = ' '.join(e.argv[1:]) # get all but the first word
					bts = spx.encode(enc)      # encode it to bytes
					
					# handle the command
					if cmd == 'b64':
						self.reply(e, b64.encode(bts).decode(enc))
					elif cmd == 'b64d':
						self.reply(e, b64.decode(bts).decode(enc))
					elif cmd == 'b32':
						self.reply(e, b32.encode(bts).decode(enc))
					elif cmd == 'b32d':
						self.reply(e, b32.decode(bts).decode(enc))
					elif cmd == 'b16':
						self.reply(e, b16.encode(bts).decode(enc))
					elif cmd == 'b16d':
						self.reply(e, b16.decode(bts).decode(enc))
					
					if e.reply:
						return
			
			except IndexError:
				trix.display (["IndexError", xdata()])
				pass
			
			
			#
			# CALC - Math evaluation
			#  - If we got this far, then the whole line is meant for 
			#    evaluation and it doesn't begin with a non-string, we'll 
			#    have to do the eval here.
			#  - This wasn't handled above because the first part of the
			#    equation is a string (eg, a variable or math function).
			#  - And again, `raise_errors` should not be passed as true
			#    because without the explicit "calc" command, we can't be
			#    sure that whatever it is that triggered the error was 
			#    actually intended to be part of a matheval calculation.
			#    (It might be something that makes sense to some other
			#     plugin that hasn't yet had a chance to execute.)
			#
			if not e.reply:
				self.reply(e, self.__calc(e))
			
				
		except Exception as ex:
			
			# get exception info
			typ = str(type(ex))
			err = str(ex)
			
			# reply debugging
			msg = "%s: %s" % (str(typ), err)
			self.error(e, dict(
					etype=typ, msg=msg, xdata=xdata(), tb=trix.tracebk(),
					source="app.plugin.calc"
				))
			
			raise
			
			#
			# IN THE EVENT OF ERRORS!
			# 
			# WE CAN'T RAISE ERRORS HERE BECAUSE THEY WOULD DISRUPT OTHER
			# PLUGINS THAT MIGHT BE ABLE TO MAKE SENSE OF WHATEVER THE 
			# INPUT IS.
			# 
			# If you spot an error specific to this plugin, check the
			# `e.error` property on return - this should give you fairly
			# extensive exception information.
			#
			# (Yes, I just spent a lot of time debugging something and,
			#  when done fixing the problem, realized this would really
			#  have helped a lot!)
			#
	
	
	
	
	#
	# CALC - Calculate equation result
	#
	def __calc(self, e, raise_errors=False):
		try:
			args = []
			for a in e.argv:
				args.append(str(a))
			return matheval(" ".join(args))
		except Exception as ex:
			#
			# This error must be ignored by "auto" calculating, else
			# every line typed (other than valid math equations) would 
			# raise errors!
			# 
			# HOWEVER...
			# If the command calc was given, we must raise errors, so
			# the calc.handle method must pass err=True..
			#
			if raise_errors:
				raise type(ex)("invalid-equation", xdata(
						source="trix.app.plugin.calc", method="__calc",
						text=" ".join(args)
					))
		
	
	
	
	#
	# IS-TEMP-C - Is the given character a temperature code?
	#
	def __istempc(self, a1):
		if len(a1)==3:
			a=a1.lower()
			if (a[0] in 'fkc') and (a[2] in 'fkc') and (a[0]!=a[2]):
				return a[1]=='2'



