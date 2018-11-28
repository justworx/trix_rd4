#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from trix.util.compenc import * 

assert(b64.encode(b"abc") == b'YWJj')
assert(b64.decode(b"YWJj") == b'abc')
assert(b64.sencode(b"abc") == b'YWJj')
assert(b64.sdecode(b"YWJj") == b'abc')
assert(b64.uencode(b"abc") == b'YWJj')
assert(b64.udecode(b"YWJj") == b'abc')
assert(b32.encode(b"abc") == b'MFRGG===')
assert(b32.decode(b'MFRGG===') == b'abc')
assert(b16.encode(b"abc") == b'616263')
assert(b16.decode(b'616263') == b'abc')

assert(hex.encode(b"abc") == b"616263")
assert(hex.decode(b"616263") == b"abc")

assert(zlib.encode(b"abc") == b"x\x9cKLJ\x06\x00\x02M\x01'")
assert(zlib.decode(b"x\x9cKLJ\x06\x00\x02M\x01'") == b"abc")

assert(bz2.encode(b"abc") == b'BZh91AY&SYd\x8c\xbbs\x00\x00\x00\x01\x008\x00 \x00!\x98\x19\x84aw$S\x85\t\x06H\xcb\xb70')
assert(bz2.decode(b'BZh91AY&SYd\x8c\xbbs\x00\x00\x00\x01\x008\x00 \x00!\x98\x19\x84aw$S\x85\t\x06H\xcb\xb70') == b"abc")

assert(compact("abc") == b'eJxLTEoGAAJNASc=')
assert(expand(b'eJxLTEoGAAJNASc=') == b'abc')

