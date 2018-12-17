

python3

from trix.net.server import *
srv = Server(9999)

from trix.net.connect import *
con = Connect(9999)

from trix.x.console import *
Console(wrap=con).console()


