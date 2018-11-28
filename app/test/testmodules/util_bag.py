
from trix.util.bag import *

x = Bag(int)
x.add('Bag-int', 1)
x.add('Bag-int', 2)
assert(x['Bag-int'] == 3)

x = Bag(list)
x.append('Bag-list', 'foo')
x.append('Bag-list', 'bar')
assert(x['Bag-list'] == ['foo', 'bar'])


