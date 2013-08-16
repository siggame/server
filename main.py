#!/usr/bin/env python2

from twisted.internet import epollreactor
epollreactor.install()
import timer

from twisted.internet import protocol, reactor
from json_protocol import JSONProtocol

if __name__ == '__main__':
    port = 19000
    f = protocol.ServerFactory()
    f.protocol = JSONProtocol
    reactor.listenTCP(port, f)
    timer.install()
    reactor.run()
