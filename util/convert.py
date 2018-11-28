#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#



convertTo = {
	
	# to C from F, K
	"c" : {
		"f" : lambda f: (f-32)*5.0/9.0,
		"k" : lambda k: k - 273.15
	},
	
	# to F from C, K
	"f" : {
		"c" : lambda c: c*(9/5)+32,
		"k" : lambda k: k*(9/5)-459.67
	},
	
	# to K from F, C
	"k" : {
		"f" : lambda f: (f+459.67)*5/9,
		"c" : lambda c: c + 273.15
	}
}


class Convert(object):
	
	def temp(self, to, frm, temp):
		to = to[0].lower()
		fm = frm[0].lower()
		eq = convertTo[to][fm]
		return eq(temp)

