#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from .xinput import *


class Form(object):
	"""Command-line data entry form."""
	
	def __init__(self, config=None, **k):
		"""
		Pass config dict that contains a "desc" dict and a "keys" list.
		The "desc" dict is required. It must contain a set of 
		name:description pairs. 
		
		Eg,.
		{
			"desc" : {
				"name" : "What's your name?",
				"age"  : "How old are you?"
			},
			"keys" : ["name", "age"]
		}
		
		The "keys" list is the order in which the discriptions are shown, 
		then followed by an input prompt. If a keys list is not provided,
		questions are ordered by the result of desc.keys().
		
		If configured "mode" is "json", each line entered must be json
		formatted and return dict elements will be typed. Remember, in
		this case, that json encoding rules apply. Eg., strings must be
		enclosed in "double-quotes", etc...
		"""
		
		config = config or {}
		config.update(**k)
		
		self.config = config
		self.prompt = config.get("prompt", "> ")
		
		self.desc = config['desc']
		self.keys = config.get('keys', self.desc.keys())
		self.mode = config.get('mode', '').lower()
		
		self.__json = self.mode == 'json'
	
	
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
		r = {}
		for key in self.keys:
			print("%s: %s" % (key, self.desc[key]))
			x = xinput(self.prompt)
			if self.__json:
				x = trix.jparse(x)
			r[key] = x
			print()
		
		return r
	
