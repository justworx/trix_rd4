#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

# UNDER CONSTRUCTION!
# This will eventually be moved to app.cline, I guess

from trix import *
from trix.util.xiter import *


if __name__ == '__main__':

	
	f = trix.path('data/unicode/UCD.zip').wrapper(member="LineBreak.txt", encoding="utf8")
	r = f.reader(member="LineBreak.txt", encoding="utf_8")
	
	R = {}
	R = trix.ncreate('util.bag.Bag', list)
	
	#
	# Loop through lines collecting values
	#
	for line in r.lines:
	  if (not line.strip()) or (line[0]=='#'):
	    pass
	  else:
	    rc = line.split("#")[0]
	    rc = rc.split(";")
	    code = rc[1].strip()
	    rval = rc[0].split('.')
	    
	    rval0 = '0x'+rval[0]
	    try:
	      rval2 = '0x'+rval[2]
	      R[code].append([rval0,rval2])
	    except:
	      R[code].append(rval0)
	
	
	#
	# Now write OUTPUT file
	#
	
	f = trix.path("trix/data/udata/OUTPUT.py").wrapper()
	w = f.writer(encoding="utf_8")
	
	# open the dict
	w.write("\n\n\nLINEBREAK = {")
		
	keycomma = ''
	
	# loop through keys
	for key in sorted(R.dict.keys()):
		
		comma = '' # start each key with no commas
		
		# write this key
		w.write(keycomma + "\n\t'" + key + "' : [")
		
		# write all this key's items
		items = xiter(iter(R.dict[key]))
		
		# ...write each item's contents.
		for ii in items:
			if isinstance(ii, list):
				w.write(comma + "[" + ii[0] + ',' +  ii[1] + ']')
			else:
				w.write(comma + ii)
			
			comma = ','
		
		w.write("]")
		keycomma = ','
	
	# close the dict
	w.write( ("\n}\n\n") )


