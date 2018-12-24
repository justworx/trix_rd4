
python3

from trix.data.cursor import *

c = Cursor((12,34,56), use=lambda p: p.set(9))
c.fetch()
