
#
# This will handle Runner, Output, and Signal(s)
#

from trix.util.runner import *

class TestRunner(Runner):
	"""
	Test Runner features. Set TestRunner.test to any string; it will 
	be written using `self.writeline()` on the next call to io(), and
	then reset to None.
	"""
	
	test = None
	
	def io(self):
		if self.test:
			self.output(self.test)
			self.test = None
	


o = Buffer(encoding='utf8')
r = TestRunner(encoding='utf_8', output=o)

assert(not r.active)
assert(not r.running)
assert(not r.threaded)


r.start()


time.sleep(0.1+r.sleep)
assert(r.active)
assert(r.running)
assert(r.threaded)


r.test = "Test 1"

time.sleep(0.1+r.sleep)
assert(o.read() == "Test 1\r\n")


r.pause()


r.test = "Test 2"
time.sleep(0.1+r.sleep)
assert(r.buffer.read() == "Test 2\r\n")


r.shutdown()
assert(not r.active)
assert(not r.running)
assert(not r.threaded)


