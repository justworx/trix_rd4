#
# Copyright 2015 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import xdata


#
# DATA QUERY
#
def dq(data, query, *args):
	"""
	Follow a path through dict and/or list objects and return a value.
	- The dd argument is a dict or list-like object.
	- The query arg is an array listing each step. It can also be a 
	  string in the form of a file path*, eg '/dogs/shepherds/german'.
	- Examples:
	  >>> dd = {'A':{'b':[9,8,7]}}
	  >>> dq(dd, ['A'])    # {'b':[9,8,7]}
	  >>> dq(dd, '/A/b/1') # 8
	  >>> dq(dd, '/a')     # Exception! No 'a' key.
	
	* In fact, you can substitute the / with any single character. The 
	  first character of the string is used to split the rest of the 
	  string into a list. For example:
	  >>> dq(dd,'.A.b.2') # 7
	  >>> dq(dd,'xAxbx1') # 8
	  >>> dq(dd,' A b 0') # 9
	"""
	path = []
	
	#
	# The query may be given as a string in which the first character
	# is the taken as the path separator.
	#
	if isinstance(query, str) and query:
		query = query[1:].split(query[0])
	
	# loop through each path element 
	for aa in iter(query):
		path.append(aa)
		if isinstance(data, dict):
			if aa in data.keys():
				data = data[aa]
			else:
				raise KeyError(path)
		else:
			aa = int(aa)
			if aa < len(data):
				data = data[aa]
			else:
				raise IndexError(path)
	
	return data

