#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ....fmt import *


# FORMAT
f = Format('{0}, {1}, {2}')
assert(f.format("bob's", "your", "Uncle!")=="bob's, your, Uncle!")

compact_bytes = f.compact("bob's", "your", "Uncle!")
assert(compact_bytes == b"eJxLyk9SL9ZRqMwvLdJRCM1LzklVBABAAgZN")

expanded_bytes = f.expand(b"eJxLyk9SL9ZRqMwvLdJRCM1LzklVBABAAgZN")
assert(expanded_bytes == b"bob's, your, Uncle!")


# JSON
d = {'a':1, 'b':9, 'c':4}
k = dict(sort_keys=True)
assert(JSON(**k).format(d) == '{"a": 1, "b": 9, "c": 4}')
assert(JDisplay(**k).format(d)=='{\n  "a": 1,\n  "b": 9,\n  "c": 4\n}')
assert(JCompact(**k).format(d)=='{"a":1,"b":9,"c":4}')


#LIST/GRID/TABLE
assert(List().format("a b c".split()) == '1  a\n2  b\n3  c')
assert(Grid().format([[1,2],[3,4]]) == '1  2\n3  4')
assert(Table(width=2).format([1,2,3,4,5])=='1  2\n3  4\n5   ')







