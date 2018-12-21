#
# There's a problem with this one! Doesn't work with the relative
# path import.
# 
# I'm going to try fixing all the others and then hope those fixes
# will resolve this problem. The static import is probably in 
# __main__ or something __main__ depends on. cline/launch, I'll bet.
#
#
"""
from .... import *

p = trix.nprocess("net.server.Server", 0).launch('run')
time.sleep(1)

try:
	status = p.rstatus()
	pid = p.pid
	
	port = status.get("reply", {}).get("server", {}).get("port")
	c = trix.ncreate("net.connect.Connect", port)
	c.write("TEST\r\n")
	
	time.sleep(0.1)
	assert(c.read() == "TEST\r\n")

except Exception as ex:
	trix.display(str(ex), xdata())

finally:
	if p:
		p.shutdown()

"""
