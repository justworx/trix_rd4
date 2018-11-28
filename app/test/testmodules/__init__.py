

#
# small tests here
#


# UTIL.BOM
from trix.util.bom import *
assert(testbom("abc".encode("utf32")).startswith('utf_32'))
assert(testbom("abc".encode("utf16")).startswith('utf_16'))
assert(testbom("abc".encode("utf_8_sig")) == "utf_8_sig")


# UTIL.CONVERT
from trix.util.convert import *
assert(Convert().temp('f', 'c', 0) == 32)
assert(Convert().temp('c', 'f', 32) == 0)


# UTIL.ENCODED (bom detection is already done, above)
from trix.util.encoded import *
tests = [
	b"Test-garbage < charset = utf_8 > blah-blah",
	b'Test-garbage < encoding= "utf_8" > blah-blah',
	b"Test-garbage < encoding ='utf_8' > blah-blah"
]
for test in tests:
	assert(Encoded(test).detect()) == 'utf_8'


# UTIL.DQ
from trix.util.dq import *
dd = {'A':{'b':[9,8,7]}}
assert(dq(dd, ['A']) == {'b':[9,8,7]})
assert(dq(dd, '/A/b/1') == 8)


# UTIL.LINEQ
from trix.util.lineq import *
q = LineQueue(encoding='utf_8')
q.feed("Abcd\r\n123")
assert(q.q.get() == "Abcd\r\n")
assert(q.fragment == '123')


# UTIL.MATHEVAL
from trix.util.matheval import *
assert(matheval("1+2") == 3)


# UTIL.MIME
from trix.util.mime import *
assert(Mime("test.txt").guess == ('text/plain', None))



# -------- TEMPORARILY OR PERMANENTLY UNTESTABLE --------

#
# UTIL.FORM
# - I can't think of a way to automatically test Form.
#

#
# UTIL.NETWORK
# - I can't think of a way to automatically test this one, either.
#

#
# UTIL.OPEN 
#  - This will be tested by the fs set of tests. The module itself
#    probably really isn't even necessary since the earliest possible
#    syntax is 2.7, where `io` is available.
#  - Need to consider getting rid of util.open.
#

#
# UTIL RUNNER and UTIL.PROCESS 
#  - I can't really test these right now. Runner needs a rewrite.
#  - I don't think Process can be tested at all until Server and 
#  - Connect are available.
#

#
# SAK
#  - This one's more of a debug tool; something you'd have to eyeball
#    test, anyway.
#

#
# X-INPUT
#  - Due to its pnature, this is not prone to automatic testing.
#

#
# X-INSPECT
#  - The testing of this will be part of the 'util.wrap' testing,
#    or vice-versa.
#

#
# X-ITER
#  - Testing of this alone is impossible as its implementation is
#    tied to whatever object it's covering.
#  - It will certainly be tested with data.scan and udata.query.
#

#
# X-JSON
#  - Too generic and ubiquitous to be "stand-alone" tested.
#

#
# X-QUEUE
#  - just a simple pair of import statement for py2/3 compatibility.
#


#
# ---------- TESTING OF UTIL.SOCK and UTIL.STREAM ----------
#
# The util.sock and util.stream modules are (or will soon be) used
# almost exclusively as support for implementation of a large set
# of classes. Their testing will be tied completely to the testing
# of those other classes.
#

