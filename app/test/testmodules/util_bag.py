#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from ....util.bag import *

x = Bag(int)
x.add('Bag-int', 1)
x.add('Bag-int', 2)
assert(x['Bag-int'] == 3)

x = Bag(list)
x.append('Bag-list', 'foo')
x.append('Bag-list', 'bar')
assert(x['Bag-list'] == ['foo', 'bar'])


