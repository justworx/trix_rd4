

python3


from trix.x.feed import *
import socket

a,b = socket.socketpair()

fsource=Feed()
fsource.set(FeedSock(fsource, a))

fsource.feed(b"a2b")

#b.recv(99)


