"""
Connection is being very resistent to performing as I intend. I think
it still has to do with config. Something's *not* happening before
the call to Config.__init__ in Connection.open ... maybe. I've lost,
for now, whatever mojo usually lets me solve such problems. I've had
a good run, but I may need to give the ol' brain a break for a while.
"""

python3

from trix.net.server import *
from trix.x.connection import *

s = Server(9999).starts()
c = Connection(9999)

c.config
c.rconfig


