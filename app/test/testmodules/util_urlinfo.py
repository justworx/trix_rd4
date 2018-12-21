
#
# This also covers util.wrap and util.inspect, at least to some
# degree... good enough for a first draft of this test suite.
#


from ....util.urlinfo import *
from ....util.wrap import Wrap


u = urlinfo("http://example.com:9999/test?foo=bar")

w = Wrap(u)
for key in u.dict:
	assert(u.dict[key] == w(key)) 


u = urlinfo("https://bob:sue@example.com/test?foo=bar", 
				password='Jelly'
			)

# make sure port is auto-detected
assert(u.port==443)

# make sure kwargs override parsed values
assert(u.password=='Jelly')


