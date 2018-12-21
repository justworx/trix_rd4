#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from ....util.enchelp import *


eh = EncodingHelper(encoding='utf8', errors="replace")
assert(eh.ek == {'encoding': 'utf_8', 'errors': 'replace'})

d = {'foo':'bar', 'errors':'ignore'}
assert(eh.extractEncoding(d) == {
		'encoding': 'utf_8', 'errors': 'ignore'
	})

d = {'foo':'bar', 'encoding':'ascii'}
assert(eh.extractEncoding(d) == {
		'encoding':'ascii', 'errors':'replace'
	})

d = {'foo':'bar', 'encoding':'ascii'}
assert(eh.extractEncoding(d) == {
		'encoding':'ascii', 'errors':'replace'
	})

d = {'foo':'bar'}
assert(eh.extractEncoding(d) == {
		 'encoding': 'utf_8', 'errors': 'replace'
	})

assert(eh.encode(b"abc") == b"abc")
assert(eh.encode("abc") == b"abc")
assert(eh.decode(b"abc") == "abc")
assert(eh.decode("abc") == "abc")



d = {'foo':'bar', 'encoding': 'utf_8', 'errors': 'replace'}
assert(eh.sansEncoding(d) == {'foo': 'bar'})


#
# much more could be tested here, but this covers the basic needs
#


