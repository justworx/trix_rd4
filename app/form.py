#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

"""
from trix.app.form import *
f = Form("x/irc/config/irc_config.conf")
f.fill()

"""

from ..util.xinput import *
from ..fmt.lines import *


class Form(object):
	"""Command-line data entry form."""
	
	def __init__(self, config=None, **k):
		"""
		Pass config dict that contains a "desc" dict and a "keys" list.
		The "desc" dict is required. It must contain a set of 
		{name:description} pairs with the following parameters:
			* field (required) is the field title
			* desc (optional) may provide additional description/detail.
			* type (default "str") can be set to typecast the given value,
				Eg,.
				{
					# name field
					"name" : {
						"field" : "Full Name",
						"desc" : "First Middle Last"
					},
					
					# age field
					"age"  : {
						"field" : "Age",
						"desc" : "How old are you?",
						"type " : "float"
					}
				}
		
		The "keys" list is the order in which the discriptions are shown, 
		then followed by an input prompt. If a keys list is not provided,
		questions are ordered by the result of desc.keys().
		
		If configured "mode" is "json", each line entered must be json
		formatted and return dict elements will be typed. Remember, in
		this case, that json encoding rules apply. Eg., strings must be
		enclosed in "double-quotes", etc...
		"""
		
		config = trix.nconfig(config, **k)
		
		# tools
		self.__lines = Lines()
		
		# init properties
		self.__prompt = config.get("prompt", "--> ")
		self.__title = config.get("title", "")
		self.__about = config.get("about", "")
		self.__fields = config.get("fields", {})
		self.__keys   = config.get("keys", sorted(config.keys()))
		self.__mode = config.get('mode', "")
		self.__cancel = config.get('cancel', "Form Cancel.")
	
	
	
	@property
	def lines(self):
		return self.__lines
	
	
	@property
	def prompt(self):
		return self.__prompt
	
	@property
	def title(self):
		return self.__title
	
	@property
	def about(self):
		return self.__about
		
	@property
	def fields(self):
		return self.__fields
	
	@property
	def keys(self):
		return self.__keys
	
	@property
	def cancel(self):
		return self.__cancel
	
	
	
	#
	# FIELD
	#
	def field(self, fieldname):
		return self.__fields[fieldname]
	
	
	#
	# FILL
	#
	def fill(self):
		"""
		Accepts input for each description in `self.desc`, as ordered by
		`self.keys`.
		
		Returns a dict containing field-names as keys and input values is 
		returned. All values are unicode, and converted to 'NFC' normal
		form.
		"""
		try:
			return self.__fill()
		except (EOFError, KeyboardInterrupt):
			if self.__cancel:
				print ("\n%s\n" % self.__cancel)
			return None
	
	
	#
	# __FILL
	#
	def __fill(self):
		
		# display form title and "about" description
		if self.title:
			self.lines.output(self.title, format="title")
		if self.about:
			self.lines.output(self.about, format="about")
		
		#
		# Add '#' and skip a space.
		#  - this needs to be handled by Lines :-/
		#
		print('#\n')
		
		# storage for addition of return values
		r = {}
		
		# localized fields
		f = self.fields
		
		# loop through keys entering values
		for key in self.keys:
			
			# single field-entry values
			fdict = f.get(key)
			xf = xfield   = fdict['field']             # field name
			xd = xdesc    = fdict.get('desc')          # field desc
			xm = xmode    = fdict.get('mode', '')      # field mode
			xt = xtype    = fdict.get('type', 'str')   # field type
			xr = xrequire = fdict.get('require', 0)    # required?
			xx = xdefault = fdict.get('default')       # default
			
			while not key in r:
				# show the Field Name / Description
				
				xxd = "; default='%s'"%xdefault if xdefault else ''
				xrr = "; required" if (xr and not xxd) else ''
				
				print ("{} ({}{}{})\n  * {}".format(xf, xt, xrr, xxd, xd))
				
				try:
					# get user input
					x = xinput(self.prompt)
					
					# set default if no value given
					if xx and not x.strip():
						x = xx
					
					if (xr and (not str(x).strip())):
						raise ValueError("Field '%s' is required." % key)
					
					if 'json' in [self.__mode, xm]:
						x = trix.jparse(x)
					elif xt != 'str':
						xtype = trix.nvalue(xt)
						x = xtype(x)
					
					r[key] = x
					
				except ValueError as ex:
					print ("; ".join(ex.args))
					print ("Ctrl-c to cancel.\n")
			
			print ('')
		
		return r




