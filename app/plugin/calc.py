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
			
			# The command's been handled, so return immediately.
			return
		
		#
		# If we got this far, the command is a string, so handle it 
		# normally - the old-fashioned way - with all args being string.
		#
		try:
			# make a list of arguments
			args = []
			for a in e.argvl:
				args.append(str(a))
		
			
			# MATH
			if cmd in ['calc', 'calculate']:
				self.reply(e, str(matheval(' '.join(args[1:]))))
				return
			
			
			# CONVERT
			if self.__istempc(cmd):
				try:
					ctemp = Convert().temp(cmd[2], cmd[0], float(e.argv[1]))
					self.reply(e, str(ctemp)+cmd[2].upper())
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
			#
			"""
			#
			# I need to figure a way to do this passive stuff without
			# breaking everything.
			#
			if not e.reply:
				self.reply(e, self.__calc(e))
			"""
				
		except Exception as ex:
			
			# get exception info
			typ = str(type(ex))
			err = str(ex)
			
			# interpreter debugging
			self.debug("command plugin error", typ, err)
			
			# reply debugging
			msg = "%s: %s" % (str(typ), err)
			self.reply(e, msg)
			
			#raise
	
	
	
	
	#
	# CALC - Calculate equation result
	#
	def __calc(self, e):
		args = []
		for a in e.argv:
			args.append(str(a))
		return matheval(" ".join(args))
	
	
	
	#
	# IS-TEMP-C - Is the given character a temperature code?
	#
	def __istempc(self, a1):
		if len(a1)==3:
			a=a1.lower()
			if (a[0] in 'fkc') and (a[2] in 'fkc') and (a[0]!=a[2]):
				return a[1]=='2'



