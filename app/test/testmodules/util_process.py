



from trix import *

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


